// OptiMOB — email de confirmação da lista de espera.
//
// Chamada por um Database Webhook do Supabase sempre que entra uma linha nova em public.lista_espera.
// Envia o email através do Resend (https://resend.com).
//
// Segredos necessários (Supabase › Edge Functions › Secrets) — nunca no código nem no GitHub:
//   RESEND_API_KEY   chave da API do Resend
//   WEBHOOK_SECRET   texto aleatório; o webhook envia-o no cabeçalho "x-webhook-secret"
// Opcionais:
//   EMAIL_FROM       remetente, por omissão "OptiMOB <ola@optimobsystem.com>" (domínio verificado no Resend)
//   EMAIL_REPLY_TO   resposta, por omissão "optimobsystem@gmail.com"
//
// Línguas (coluna "idioma"): pt, en, es, fr, ru, ar, vi, zh, de, it, nl, pl, tr, el, uk, ro, cs, sk, hu, sv, da, nb, fi, mk, bg, sr, hr, he, fa, ur, hi, bn, id, ms, th, ja, ko, sw, fil.
// Outra língua: inglês. Sem idioma (inscrições antigas): português + inglês.

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const WEBHOOK_SECRET = Deno.env.get("WEBHOOK_SECRET") ?? "";
const FROM = Deno.env.get("EMAIL_FROM") ?? "OptiMOB <ola@optimobsystem.com>";
const REPLY_TO = Deno.env.get("EMAIL_REPLY_TO") ?? "optimobsystem@gmail.com";

const esc = (s: string) =>
  s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));

// Textos do email em cada língua suportada. "idioma" vem do site (língua em que a página estava
// quando a pessoa se inscreveu, incluindo páginas traduzidas pelo navegador).
type T = { subject: string; label: string; h1: string; p1: string; p2: string; p3: string; foot: string; perfis: string[] };
const PERFIS = ["Marcenaria", "Designer de interiores", "Fábrica de mobiliário", "Outro"];
const L: Record<string, T> = {
  pt: {
    subject: "Está na lista de espera do OptiMOB", label: "Acesso antecipado", h1: "Está na lista de espera.",
    p1: "Obrigado pelo interesse no OptiMOB, a extensão de blocos paramétricos de marcenaria para SketchUp.",
    p2: "Registámos {e} ({p}). Quando a versão de teste estiver pronta, enviamos-lhe as instruções de instalação para este email.",
    p3: "Tem alguma pergunta? Basta responder a este email.",
    foot: 'Recebeu este email porque se inscreveu na lista de acesso antecipado em optimobsystem.com. Para sair da lista e apagar os seus dados, responda com "remover".',
    perfis: PERFIS,
  },
  en: {
    subject: "You're on the OptiMOB waitlist", label: "Early access", h1: "You're on the waitlist.",
    p1: "Thank you for your interest in OptiMOB, the parametric joinery blocks extension for SketchUp.",
    p2: "We registered {e} ({p}). When the beta is ready, we will send the installation instructions to this address.",
    p3: "Any questions? Just reply to this email.",
    foot: 'You received this email because you joined the early access list at optimobsystem.com. To leave the list and delete your data, reply with "remove".',
    perfis: ["Joinery / woodworking shop", "Interior designer", "Furniture factory", "Other"],
  },
  es: {
    subject: "Estás en la lista de espera de OptiMOB", label: "Acceso anticipado", h1: "Estás en la lista de espera.",
    p1: "Gracias por tu interés en OptiMOB, la extensión de bloques paramétricos de carpintería para SketchUp.",
    p2: "Hemos registrado {e} ({p}). Cuando la versión de prueba esté lista, te enviaremos las instrucciones de instalación a este correo.",
    p3: "¿Tienes alguna pregunta? Solo responde a este correo.",
    foot: 'Recibes este correo porque te inscribiste en la lista de acceso anticipado en optimobsystem.com. Para salir de la lista y borrar tus datos, responde con "eliminar".',
    perfis: ["Carpintería / taller", "Diseñador/a de interiores", "Fábrica de muebles", "Otro"],
  },
  fr: {
    subject: "Vous êtes sur la liste d'attente d'OptiMOB", label: "Accès anticipé", h1: "Vous êtes sur la liste d'attente.",
    p1: "Merci de votre intérêt pour OptiMOB, l'extension de blocs paramétriques de menuiserie pour SketchUp.",
    p2: "Nous avons enregistré {e} ({p}). Dès que la version de test sera prête, nous vous enverrons les instructions d'installation à cette adresse.",
    p3: "Une question ? Répondez simplement à cet e-mail.",
    foot: "Vous recevez cet e-mail car vous vous êtes inscrit(e) à la liste d'accès anticipé sur optimobsystem.com. Pour quitter la liste et supprimer vos données, répondez « supprimer ».",
    perfis: ["Menuiserie / atelier", "Architecte d'intérieur", "Fabrique de meubles", "Autre"],
  },
  ru: {
    subject: "Вы в списке ожидания OptiMOB", label: "Ранний доступ", h1: "Вы в списке ожидания.",
    p1: "Спасибо за интерес к OptiMOB — расширению параметрических столярных блоков для SketchUp.",
    p2: "Мы зарегистрировали {e} ({p}). Когда тестовая версия будет готова, мы отправим инструкции по установке на этот адрес.",
    p3: "Есть вопросы? Просто ответьте на это письмо.",
    foot: "Вы получили это письмо, потому что записались в список раннего доступа на optimobsystem.com. Чтобы выйти из списка и удалить свои данные, ответьте словом «удалить».",
    perfis: ["Столярная мастерская", "Дизайнер интерьеров", "Мебельная фабрика", "Другое"],
  },
  ar: {
    subject: "أنت على قائمة انتظار OptiMOB", label: "وصول مبكر", h1: "أنت على قائمة الانتظار.",
    p1: "شكرًا لاهتمامك بـ OptiMOB، إضافة كتل النجارة البارامترية لبرنامج SketchUp.",
    p2: "سجّلنا {e} ({p}). عندما تصبح النسخة التجريبية جاهزة، سنرسل تعليمات التثبيت إلى هذا البريد.",
    p3: "هل لديك أي سؤال؟ ما عليك سوى الرد على هذه الرسالة.",
    foot: "وصلتك هذه الرسالة لأنك سجّلت في قائمة الوصول المبكر على optimobsystem.com. لمغادرة القائمة وحذف بياناتك، ردّ بكلمة «إزالة».",
    perfis: ["ورشة نجارة", "مصمم ديكور داخلي", "مصنع أثاث", "أخرى"],
  },
  vi: {
    subject: "Bạn đã có tên trong danh sách chờ OptiMOB", label: "Truy cập sớm", h1: "Bạn đã có tên trong danh sách chờ.",
    p1: "Cảm ơn bạn đã quan tâm đến OptiMOB, tiện ích mở rộng khối mộc tham số cho SketchUp.",
    p2: "Chúng tôi đã ghi nhận {e} ({p}). Khi bản dùng thử sẵn sàng, chúng tôi sẽ gửi hướng dẫn cài đặt đến địa chỉ này.",
    p3: "Bạn có câu hỏi? Chỉ cần trả lời email này.",
    foot: 'Bạn nhận được email này vì đã đăng ký danh sách truy cập sớm tại optimobsystem.com. Để rời danh sách và xóa dữ liệu của bạn, hãy trả lời "xóa".',
    perfis: ["Xưởng mộc", "Nhà thiết kế nội thất", "Nhà máy nội thất", "Khác"],
  },
  zh: {
    subject: "您已加入 OptiMOB 候补名单", label: "抢先体验", h1: "您已加入候补名单。",
    p1: "感谢您关注 OptiMOB——一款用于 SketchUp 的参数化木作组件扩展。",
    p2: "我们已登记 {e}（{p}）。测试版准备就绪后，我们会将安装说明发送到此邮箱。",
    p3: "有任何问题？直接回复此邮件即可。",
    foot: "您收到此邮件是因为您在 optimobsystem.com 加入了抢先体验名单。如需退出名单并删除您的数据，请回复“删除”。",
    perfis: ["木工作坊", "室内设计师", "家具工厂", "其他"],
  },
  de: {
    subject: "Sie stehen auf der Warteliste von OptiMOB", label: "Früher Zugang", h1: "Sie stehen auf der Warteliste.",
    p1: "Vielen Dank für Ihr Interesse an OptiMOB, der Erweiterung mit parametrischen Schreinerei-Bausteinen für SketchUp.",
    p2: "Wir haben {e} ({p}) registriert. Sobald die Testversion bereit ist, senden wir die Installationsanleitung an diese Adresse.",
    p3: "Fragen? Antworten Sie einfach auf diese E-Mail.",
    foot: "Sie erhalten diese E-Mail, weil Sie sich auf optimobsystem.com für den frühen Zugang eingetragen haben. Um die Liste zu verlassen und Ihre Daten zu löschen, antworten Sie mit „entfernen“.",
    perfis: ["Schreinerei / Werkstatt", "Innenarchitekt/in", "Möbelfabrik", "Sonstiges"],
  },
  it: {
    subject: "Sei nella lista d'attesa di OptiMOB", label: "Accesso anticipato", h1: "Sei nella lista d'attesa.",
    p1: "Grazie per l'interesse verso OptiMOB, l'estensione di blocchi parametrici di falegnameria per SketchUp.",
    p2: "Abbiamo registrato {e} ({p}). Quando la versione di prova sarà pronta, invieremo le istruzioni di installazione a questo indirizzo.",
    p3: "Hai domande? Rispondi semplicemente a questa email.",
    foot: "Ricevi questa email perché ti sei iscritto/a alla lista di accesso anticipato su optimobsystem.com. Per uscire dalla lista e cancellare i tuoi dati, rispondi con «rimuovi».",
    perfis: ["Falegnameria / laboratorio", "Interior designer", "Fabbrica di mobili", "Altro"],
  },
  nl: {
    subject: "Je staat op de wachtlijst van OptiMOB", label: "Vroege toegang", h1: "Je staat op de wachtlijst.",
    p1: "Bedankt voor je interesse in OptiMOB, de extensie met parametrische meubelmakersblokken voor SketchUp.",
    p2: "We hebben {e} ({p}) geregistreerd. Zodra de testversie klaar is, sturen we de installatie-instructies naar dit adres.",
    p3: "Vragen? Beantwoord gewoon deze e-mail.",
    foot: 'Je ontvangt deze e-mail omdat je je hebt aangemeld voor vroege toegang op optimobsystem.com. Om de lijst te verlaten en je gegevens te verwijderen, antwoord je met "verwijderen".',
    perfis: ["Meubelmakerij / werkplaats", "Interieurontwerper", "Meubelfabriek", "Anders"],
  },
  pl: {
    subject: "Jesteś na liście oczekujących OptiMOB", label: "Wczesny dostęp", h1: "Jesteś na liście oczekujących.",
    p1: "Dziękujemy za zainteresowanie OptiMOB — rozszerzeniem z parametrycznymi blokami stolarskimi dla SketchUp.",
    p2: "Zarejestrowaliśmy {e} ({p}). Gdy wersja testowa będzie gotowa, wyślemy instrukcję instalacji na ten adres.",
    p3: "Masz pytania? Po prostu odpowiedz na tę wiadomość.",
    foot: "Otrzymujesz tę wiadomość, ponieważ zapisałeś(-aś) się na listę wczesnego dostępu na optimobsystem.com. Aby opuścić listę i usunąć swoje dane, odpowiedz „usuń”.",
    perfis: ["Stolarnia / warsztat", "Projektant wnętrz", "Fabryka mebli", "Inne"],
  },
  tr: {
    subject: "OptiMOB bekleme listesindesiniz", label: "Erken erişim", h1: "Bekleme listesindesiniz.",
    p1: "SketchUp için parametrik marangozluk blokları eklentisi OptiMOB'a gösterdiğiniz ilgi için teşekkürler.",
    p2: "{e} ({p}) adresini kaydettik. Test sürümü hazır olduğunda kurulum talimatlarını bu adrese göndereceğiz.",
    p3: "Sorunuz mu var? Bu e-postayı yanıtlamanız yeterli.",
    foot: 'Bu e-postayı optimobsystem.com\'da erken erişim listesine kaydolduğunuz için aldınız. Listeden çıkmak ve verilerinizi silmek için "kaldır" yazarak yanıtlayın.',
    perfis: ["Marangoz atölyesi", "İç mimar", "Mobilya fabrikası", "Diğer"],
  },
  el: {
    subject: "Είστε στη λίστα αναμονής του OptiMOB", label: "Πρόωρη πρόσβαση", h1: "Είστε στη λίστα αναμονής.",
    p1: "Σας ευχαριστούμε για το ενδιαφέρον σας για το OptiMOB, την επέκταση παραμετρικών μπλοκ ξυλουργικής για το SketchUp.",
    p2: "Καταχωρίσαμε το {e} ({p}). Μόλις η δοκιμαστική έκδοση είναι έτοιμη, θα στείλουμε τις οδηγίες εγκατάστασης σε αυτή τη διεύθυνση.",
    p3: "Έχετε απορίες; Απλώς απαντήστε σε αυτό το email.",
    foot: "Λάβατε αυτό το email επειδή εγγραφήκατε στη λίστα πρόωρης πρόσβασης στο optimobsystem.com. Για να αποχωρήσετε από τη λίστα και να διαγραφούν τα δεδομένα σας, απαντήστε «διαγραφή».",
    perfis: ["Ξυλουργείο", "Διακοσμητής εσωτερικών χώρων", "Εργοστάσιο επίπλων", "Άλλο"],
  },
  uk: {
    subject: "Ви в списку очікування OptiMOB", label: "Ранній доступ", h1: "Ви в списку очікування.",
    p1: "Дякуємо за інтерес до OptiMOB — розширення параметричних столярних блоків для SketchUp.",
    p2: "Ми зареєстрували {e} ({p}). Коли тестова версія буде готова, ми надішлемо інструкції зі встановлення на цю адресу.",
    p3: "Маєте запитання? Просто дайте відповідь на цей лист.",
    foot: "Ви отримали цей лист, бо записалися до списку раннього доступу на optimobsystem.com. Щоб вийти зі списку й видалити свої дані, дайте відповідь словом «видалити».",
    perfis: ["Столярна майстерня", "Дизайнер інтер'єрів", "Меблева фабрика", "Інше"],
  },
  ro: {
    subject: "Ești pe lista de așteptare OptiMOB", label: "Acces anticipat", h1: "Ești pe lista de așteptare.",
    p1: "Îți mulțumim pentru interesul față de OptiMOB, extensia de blocuri parametrice de tâmplărie pentru SketchUp.",
    p2: "Am înregistrat {e} ({p}). Când versiunea de test va fi gata, îți vom trimite instrucțiunile de instalare la această adresă.",
    p3: "Ai întrebări? Răspunde simplu la acest e-mail.",
    foot: "Primești acest e-mail pentru că te-ai înscris pe lista de acces anticipat de pe optimobsystem.com. Pentru a ieși de pe listă și a-ți șterge datele, răspunde cu „șterge”.",
    perfis: ["Tâmplărie / atelier", "Designer de interior", "Fabrică de mobilă", "Altceva"],
  },
  cs: {
    subject: "Jste na čekací listině OptiMOB", label: "Předběžný přístup", h1: "Jste na čekací listině.",
    p1: "Děkujeme za zájem o OptiMOB, rozšíření s parametrickými truhlářskými bloky pro SketchUp.",
    p2: "Zaregistrovali jsme {e} ({p}). Jakmile bude testovací verze připravena, pošleme na tuto adresu pokyny k instalaci.",
    p3: "Máte dotaz? Stačí odpovědět na tento e-mail.",
    foot: "Tento e-mail jste obdrželi, protože jste se přihlásili na seznam předběžného přístupu na optimobsystem.com. Chcete-li ze seznamu odejít a smazat svá data, odpovězte „odstranit“.",
    perfis: ["Truhlárna / dílna", "Interiérový designér", "Továrna na nábytek", "Jiné"],
  },
  sk: {
    subject: "Ste na čakacej listine OptiMOB", label: "Predbežný prístup", h1: "Ste na čakacej listine.",
    p1: "Ďakujeme za záujem o OptiMOB, rozšírenie s parametrickými stolárskymi blokmi pre SketchUp.",
    p2: "Zaregistrovali sme {e} ({p}). Keď bude testovacia verzia pripravená, pošleme na túto adresu pokyny na inštaláciu.",
    p3: "Máte otázku? Stačí odpovedať na tento e-mail.",
    foot: "Tento e-mail ste dostali, pretože ste sa prihlásili na zoznam predbežného prístupu na optimobsystem.com. Ak chcete zo zoznamu odísť a vymazať svoje údaje, odpovedzte „odstrániť“.",
    perfis: ["Stolárstvo / dielňa", "Interiérový dizajnér", "Továreň na nábytok", "Iné"],
  },
  hu: {
    subject: "Felkerült az OptiMOB várólistájára", label: "Korai hozzáférés", h1: "Felkerült a várólistára.",
    p1: "Köszönjük, hogy érdeklődik az OptiMOB, a SketchUp-hoz készült parametrikus asztalosipari blokkbővítmény iránt.",
    p2: "Regisztráltuk ezt: {e} ({p}). Amint elkészül a tesztverzió, erre a címre küldjük a telepítési útmutatót.",
    p3: "Kérdése van? Egyszerűen válaszoljon erre az e-mailre.",
    foot: "Azért kapta ezt az e-mailt, mert feliratkozott a korai hozzáférési listára az optimobsystem.com oldalon. Ha le szeretne iratkozni és törölni szeretné adatait, válaszoljon a „törlés” szóval.",
    perfis: ["Asztalosműhely", "Belsőépítész", "Bútorgyár", "Egyéb"],
  },
  sv: {
    subject: "Du står på OptiMOB:s väntelista", label: "Tidig åtkomst", h1: "Du står på väntelistan.",
    p1: "Tack för ditt intresse för OptiMOB, tillägget med parametriska snickeriblock för SketchUp.",
    p2: "Vi har registrerat {e} ({p}). När testversionen är klar skickar vi installationsanvisningarna till den här adressen.",
    p3: "Har du frågor? Svara bara på det här mejlet.",
    foot: "Du får det här mejlet eftersom du anmält dig till listan för tidig åtkomst på optimobsystem.com. Svara med ”ta bort” för att lämna listan och radera dina uppgifter.",
    perfis: ["Snickeri / verkstad", "Inredningsarkitekt", "Möbelfabrik", "Annat"],
  },
  da: {
    subject: "Du er på OptiMOBs venteliste", label: "Tidlig adgang", h1: "Du er på ventelisten.",
    p1: "Tak for din interesse for OptiMOB, udvidelsen med parametriske snedkerblokke til SketchUp.",
    p2: "Vi har registreret {e} ({p}). Når testversionen er klar, sender vi installationsvejledningen til denne adresse.",
    p3: "Har du spørgsmål? Svar blot på denne e-mail.",
    foot: 'Du modtager denne e-mail, fordi du har tilmeldt dig listen for tidlig adgang på optimobsystem.com. Svar med "fjern" for at forlade listen og slette dine data.',
    perfis: ["Snedkeri / værksted", "Indretningsarkitekt", "Møbelfabrik", "Andet"],
  },
  nb: {
    subject: "Du står på ventelisten til OptiMOB", label: "Tidlig tilgang", h1: "Du står på ventelisten.",
    p1: "Takk for interessen for OptiMOB, utvidelsen med parametriske snekkerblokker for SketchUp.",
    p2: "Vi har registrert {e} ({p}). Når testversjonen er klar, sender vi installasjonsveiledningen til denne adressen.",
    p3: "Har du spørsmål? Bare svar på denne e-posten.",
    foot: "Du mottar denne e-posten fordi du meldte deg på listen for tidlig tilgang på optimobsystem.com. Svar med «fjern» for å forlate listen og slette dataene dine.",
    perfis: ["Snekkerverksted", "Interiørarkitekt", "Møbelfabrikk", "Annet"],
  },
  fi: {
    subject: "Olet OptiMOBin odotuslistalla", label: "Ennakkokäyttö", h1: "Olet odotuslistalla.",
    p1: "Kiitos kiinnostuksestasi OptiMOBia kohtaan – se on SketchUpin laajennus parametrisille puusepänosille.",
    p2: "Rekisteröimme osoitteen {e} ({p}). Kun testiversio on valmis, lähetämme asennusohjeet tähän osoitteeseen.",
    p3: "Onko kysyttävää? Vastaa vain tähän sähköpostiin.",
    foot: "Sait tämän viestin, koska liityit ennakkokäyttölistalle osoitteessa optimobsystem.com. Jos haluat poistua listalta ja poistaa tietosi, vastaa sanalla ”poista”.",
    perfis: ["Puusepänverstas", "Sisustussuunnittelija", "Huonekalutehdas", "Muu"],
  },
  mk: {
    subject: "Вие сте на листата на чекање на OptiMOB", label: "Ран пристап", h1: "Вие сте на листата на чекање.",
    p1: "Ви благодариме за интересот за OptiMOB, додатокот со параметарски столарски блокови за SketchUp.",
    p2: "Го регистриравме {e} ({p}). Кога тест-верзијата ќе биде подготвена, ќе ги испратиме упатствата за инсталација на оваа адреса.",
    p3: "Имате прашање? Едноставно одговорете на оваа е-порака.",
    foot: "Ја добивте оваа е-порака бидејќи се пријавивте на листата за ран пристап на optimobsystem.com. За да се откажете и да ги избришете вашите податоци, одговорете со „отстрани“.",
    perfis: ["Столарска работилница", "Дизајнер на ентериер", "Фабрика за мебел", "Друго"],
  },
  bg: {
    subject: "Вие сте в списъка с чакащи на OptiMOB", label: "Ранен достъп", h1: "Вие сте в списъка с чакащи.",
    p1: "Благодарим ви за интереса към OptiMOB — разширението с параметрични дърводелски блокове за SketchUp.",
    p2: "Регистрирахме {e} ({p}). Когато тестовата версия е готова, ще изпратим инструкциите за инсталиране на този адрес.",
    p3: "Имате въпроси? Просто отговорете на този имейл.",
    foot: "Получавате този имейл, защото се записахте в списъка за ранен достъп на optimobsystem.com. За да напуснете списъка и да изтриете данните си, отговорете с „премахни“.",
    perfis: ["Дърводелска работилница", "Интериорен дизайнер", "Мебелна фабрика", "Друго"],
  },
  sr: {
    subject: "Налазите се на листи чекања за OptiMOB", label: "Рани приступ", h1: "Налазите се на листи чекања.",
    p1: "Хвала на интересовању за OptiMOB, проширење са параметарским столарским блоковима за SketchUp.",
    p2: "Регистровали смо {e} ({p}). Када тест-верзија буде спремна, послаћемо упутства за инсталацију на ову адресу.",
    p3: "Имате питање? Само одговорите на овај имејл.",
    foot: "Добили сте овај имејл јер сте се пријавили на листу за рани приступ на optimobsystem.com. Да бисте напустили листу и обрисали своје податке, одговорите са „уклони“.",
    perfis: ["Столарска радионица", "Дизајнер ентеријера", "Фабрика намештаја", "Друго"],
  },
  hr: {
    subject: "Nalazite se na listi čekanja za OptiMOB", label: "Rani pristup", h1: "Nalazite se na listi čekanja.",
    p1: "Hvala na interesu za OptiMOB, proširenje s parametarskim stolarskim blokovima za SketchUp.",
    p2: "Registrirali smo {e} ({p}). Kada testna verzija bude spremna, poslat ćemo upute za instalaciju na ovu adresu.",
    p3: "Imate pitanje? Samo odgovorite na ovaj e-mail.",
    foot: "Primili ste ovaj e-mail jer ste se prijavili na listu ranog pristupa na optimobsystem.com. Za izlazak s liste i brisanje podataka odgovorite s „ukloni“.",
    perfis: ["Stolarska radionica", "Dizajner interijera", "Tvornica namještaja", "Ostalo"],
  },
  he: {
    subject: "נרשמת לרשימת ההמתנה של OptiMOB", label: "גישה מוקדמת", h1: "נרשמת לרשימת ההמתנה.",
    p1: "תודה על ההתעניינות ב-OptiMOB, תוסף בלוקי נגרות פרמטריים ל-SketchUp.",
    p2: "רשמנו את {e} ({p}). כשגרסת הניסיון תהיה מוכנה, נשלח את הוראות ההתקנה לכתובת הזו.",
    p3: "יש לך שאלה? פשוט השב/י למייל הזה.",
    foot: 'קיבלת מייל זה כי נרשמת לרשימת הגישה המוקדמת באתר optimobsystem.com. כדי לצאת מהרשימה ולמחוק את הנתונים שלך, השב/י "הסר".',
    perfis: ["נגרייה", "מעצב/ת פנים", "מפעל רהיטים", "אחר"],
  },
  fa: {
    subject: "شما در فهرست انتظار OptiMOB هستید", label: "دسترسی زودهنگام", h1: "شما در فهرست انتظار هستید.",
    p1: "از علاقه‌تان به OptiMOB، افزونهٔ بلوک‌های پارامتریک نجاری برای SketchUp، سپاسگزاریم.",
    p2: "ما {e} ({p}) را ثبت کردیم. وقتی نسخهٔ آزمایشی آماده شد، راهنمای نصب را به همین نشانی می‌فرستیم.",
    p3: "پرسشی دارید؟ کافی است به همین ایمیل پاسخ دهید.",
    foot: "این ایمیل را دریافت کردید چون در فهرست دسترسی زودهنگام در optimobsystem.com ثبت‌نام کرده‌اید. برای خروج از فهرست و حذف اطلاعاتتان، با کلمهٔ «حذف» پاسخ دهید.",
    perfis: ["کارگاه نجاری", "طراح داخلی", "کارخانهٔ مبلمان", "سایر"],
  },
  ur: {
    subject: "آپ OptiMOB کی انتظار فہرست میں شامل ہیں", label: "ابتدائی رسائی", h1: "آپ انتظار فہرست میں شامل ہیں۔",
    p1: "OptiMOB میں دلچسپی کا شکریہ، یہ SketchUp کے لیے پیرامیٹرک بڑھئی بلاکس کی ایکسٹینشن ہے۔",
    p2: "ہم نے {e} ({p}) درج کر لیا ہے۔ جب آزمائشی ورژن تیار ہو جائے گا تو ہم انسٹالیشن کی ہدایات اسی پتے پر بھیجیں گے۔",
    p3: "کوئی سوال ہے؟ بس اس ای میل کا جواب دیں۔",
    foot: 'آپ کو یہ ای میل اس لیے ملی کیونکہ آپ نے optimobsystem.com پر ابتدائی رسائی کی فہرست میں شمولیت اختیار کی۔ فہرست سے نکلنے اور اپنا ڈیٹا حذف کرانے کے لیے "ہٹائیں" لکھ کر جواب دیں۔',
    perfis: ["بڑھئی ورکشاپ", "انٹیریئر ڈیزائنر", "فرنیچر فیکٹری", "دیگر"],
  },
  hi: {
    subject: "आप OptiMOB की प्रतीक्षा सूची में हैं", label: "शीघ्र पहुँच", h1: "आप प्रतीक्षा सूची में हैं।",
    p1: "OptiMOB में रुचि लेने के लिए धन्यवाद — यह SketchUp के लिए पैरामीट्रिक बढ़ईगीरी ब्लॉक्स का एक्सटेंशन है।",
    p2: "हमने {e} ({p}) दर्ज कर लिया है। टेस्ट संस्करण तैयार होते ही हम इंस्टॉलेशन के निर्देश इसी पते पर भेजेंगे।",
    p3: "कोई सवाल है? बस इस ईमेल का जवाब दें।",
    foot: 'आपको यह ईमेल इसलिए मिला क्योंकि आपने optimobsystem.com पर शीघ्र पहुँच सूची में नाम लिखवाया है। सूची से हटने और अपना डेटा मिटाने के लिए "हटाएँ" लिखकर जवाब दें।',
    perfis: ["बढ़ईगीरी कार्यशाला", "इंटीरियर डिज़ाइनर", "फ़र्नीचर फ़ैक्टरी", "अन्य"],
  },
  bn: {
    subject: "আপনি OptiMOB-এর অপেক্ষমাণ তালিকায় আছেন", label: "আগাম অ্যাক্সেস", h1: "আপনি অপেক্ষমাণ তালিকায় আছেন।",
    p1: "OptiMOB-এ আগ্রহের জন্য ধন্যবাদ — এটি SketchUp-এর জন্য প্যারামেট্রিক কাঠমিস্ত্রি ব্লকের এক্সটেনশন।",
    p2: "আমরা {e} ({p}) নিবন্ধন করেছি। পরীক্ষামূলক সংস্করণ প্রস্তুত হলে ইনস্টলেশনের নির্দেশনা এই ঠিকানায় পাঠাব।",
    p3: "কোনো প্রশ্ন আছে? শুধু এই ইমেলের উত্তর দিন।",
    foot: 'আপনি optimobsystem.com-এ আগাম অ্যাক্সেস তালিকায় যোগ দিয়েছেন বলে এই ইমেল পেয়েছেন। তালিকা থেকে বের হতে ও আপনার তথ্য মুছতে "সরান" লিখে উত্তর দিন।',
    perfis: ["কাঠের কারখানা", "ইন্টেরিয়র ডিজাইনার", "আসবাব কারখানা", "অন্যান্য"],
  },
  id: {
    subject: "Anda masuk daftar tunggu OptiMOB", label: "Akses awal", h1: "Anda sudah masuk daftar tunggu.",
    p1: "Terima kasih atas minat Anda pada OptiMOB, ekstensi blok pertukangan parametrik untuk SketchUp.",
    p2: "Kami telah mendaftarkan {e} ({p}). Saat versi uji coba siap, kami akan mengirim petunjuk instalasi ke alamat ini.",
    p3: "Ada pertanyaan? Cukup balas email ini.",
    foot: 'Anda menerima email ini karena mendaftar ke daftar akses awal di optimobsystem.com. Untuk keluar dari daftar dan menghapus data Anda, balas dengan "hapus".',
    perfis: ["Bengkel kayu / mebel", "Desainer interior", "Pabrik furnitur", "Lainnya"],
  },
  ms: {
    subject: "Anda dalam senarai menunggu OptiMOB", label: "Akses awal", h1: "Anda dalam senarai menunggu.",
    p1: "Terima kasih atas minat anda terhadap OptiMOB, sambungan blok pertukangan kayu parametrik untuk SketchUp.",
    p2: "Kami telah mendaftarkan {e} ({p}). Apabila versi percubaan sedia, kami akan menghantar arahan pemasangan ke alamat ini.",
    p3: "Ada soalan? Balas sahaja e-mel ini.",
    foot: 'Anda menerima e-mel ini kerana menyertai senarai akses awal di optimobsystem.com. Untuk keluar daripada senarai dan memadam data anda, balas dengan "buang".',
    perfis: ["Bengkel pertukangan kayu", "Pereka dalaman", "Kilang perabot", "Lain-lain"],
  },
  th: {
    subject: "คุณอยู่ในรายชื่อรอของ OptiMOB แล้ว", label: "สิทธิ์ใช้งานก่อนใคร", h1: "คุณอยู่ในรายชื่อรอแล้ว",
    p1: "ขอบคุณที่สนใจ OptiMOB ส่วนขยายบล็อกงานไม้แบบพาราเมตริกสำหรับ SketchUp",
    p2: "เราได้ลงทะเบียน {e} ({p}) แล้ว เมื่อเวอร์ชันทดลองพร้อม เราจะส่งวิธีติดตั้งไปที่อีเมลนี้",
    p3: "มีคำถามไหม ตอบกลับอีเมลนี้ได้เลย",
    foot: 'คุณได้รับอีเมลนี้เพราะได้ลงชื่อในรายชื่อสิทธิ์ใช้งานก่อนใครที่ optimobsystem.com หากต้องการออกจากรายชื่อและลบข้อมูลของคุณ ให้ตอบกลับว่า "ลบ"',
    perfis: ["โรงงานงานไม้", "นักออกแบบตกแต่งภายใน", "โรงงานเฟอร์นิเจอร์", "อื่น ๆ"],
  },
  ja: {
    subject: "OptiMOB のウェイティングリストに登録されました", label: "先行アクセス", h1: "ウェイティングリストに登録されました。",
    p1: "SketchUp 用パラメトリック木工ブロック拡張機能 OptiMOB にご関心をお寄せいただき、ありがとうございます。",
    p2: "{e}（{p}）を登録しました。テスト版の準備ができ次第、このアドレスにインストール手順をお送りします。",
    p3: "ご質問があれば、このメールにご返信ください。",
    foot: "このメールは、optimobsystem.com で先行アクセスリストにご登録いただいたため送信しています。リストから退会してデータを削除するには、「削除」とご返信ください。",
    perfis: ["木工所・工房", "インテリアデザイナー", "家具工場", "その他"],
  },
  ko: {
    subject: "OptiMOB 대기자 명단에 등록되었습니다", label: "사전 체험", h1: "대기자 명단에 등록되었습니다.",
    p1: "SketchUp용 파라메트릭 목공 블록 확장 프로그램 OptiMOB에 관심을 가져 주셔서 감사합니다.",
    p2: "{e} ({p}) 주소를 등록했습니다. 테스트 버전이 준비되면 이 주소로 설치 안내를 보내 드리겠습니다.",
    p3: "궁금한 점이 있으신가요? 이 메일에 회신해 주세요.",
    foot: 'optimobsystem.com에서 사전 체험 명단에 등록하셨기 때문에 이 메일을 받으셨습니다. 명단에서 나가고 데이터를 삭제하려면 "삭제"라고 회신해 주세요.',
    perfis: ["목공방", "인테리어 디자이너", "가구 공장", "기타"],
  },
  sw: {
    subject: "Uko kwenye orodha ya kusubiri ya OptiMOB", label: "Ufikiaji wa mapema", h1: "Uko kwenye orodha ya kusubiri.",
    p1: "Asante kwa kuvutiwa na OptiMOB, kiendelezi cha vitalu vya useremala vya kiparametriki kwa SketchUp.",
    p2: "Tumesajili {e} ({p}). Toleo la majaribio likiwa tayari, tutatuma maelekezo ya usakinishaji kwa anwani hii.",
    p3: "Una swali? Jibu tu barua pepe hii.",
    foot: 'Umepokea barua pepe hii kwa sababu ulijiunga na orodha ya ufikiaji wa mapema kwenye optimobsystem.com. Ili kujiondoa na kufuta data yako, jibu kwa neno "ondoa".',
    perfis: ["Karakana ya useremala", "Mbunifu wa ndani", "Kiwanda cha samani", "Nyingine"],
  },
  fil: {
    subject: "Nasa waitlist ka na ng OptiMOB", label: "Maagang access", h1: "Nasa waitlist ka na.",
    p1: "Salamat sa iyong interes sa OptiMOB, ang extension ng mga parametric na bloke ng karpinterya para sa SketchUp.",
    p2: "Nairehistro namin ang {e} ({p}). Kapag handa na ang test version, ipapadala namin ang mga tagubilin sa pag-install sa address na ito.",
    p3: "May tanong? Sumagot lang sa email na ito.",
    foot: 'Natanggap mo ang email na ito dahil nag-sign up ka sa early access list sa optimobsystem.com. Para umalis sa listahan at burahin ang iyong data, sumagot ng "alisin".',
    perfis: ["Karpinterya / workshop", "Interior designer", "Pabrika ng muwebles", "Iba pa"],
  },
};

// Códigos que os navegadores usam para a mesma língua (ou línguas muito próximas).
const ALIAS: Record<string, string> = { no: "nb", nn: "nb", iw: "he", in: "id", tl: "fil", bs: "hr", me: "sr", ca: "es", gl: "es", be: "ru" };
const RTL = new Set(["ar", "he", "fa", "ur"]);

// "pt-BR" -> "pt"; sem idioma (inscrições antigas) -> null = português + inglês; língua sem tradução -> inglês
function lingua(idioma?: string | null): string | null {
  if (!idioma) return null;
  let c = idioma.toLowerCase().split(/[-_]/)[0];
  c = ALIAS[c] ?? c;
  return c in L ? c : "en";
}
const perfilEm = (t: T, perfil: string) => { const i = PERFIS.indexOf(perfil); return i >= 0 ? t.perfis[i] : perfil; };

const P = 'style="font-size:15px;line-height:1.6;color:#C9CDCB;margin:0 0 14px"';
const LABEL = 'style="font-family:Courier New,monospace;font-size:11px;letter-spacing:3px;color:#3AA0FF;text-transform:uppercase"';

// ---------------------------------------------------------------- grupo do WhatsApp
// Link de convite do grupo da lista de espera (pode ser trocado sem mexer no código: secret WHATSAPP_GROUP_URL).
const WA_URL = Deno.env.get("WHATSAPP_GROUP_URL") ?? "https://chat.whatsapp.com/SEU-CONVITE";

// [assunto do convite, título do convite, parágrafo, botão]
const W: Record<string, [string, string, string, string]> = {
  pt: ["O grupo do OptiMOB no WhatsApp já está aberto", "Criámos um grupo para a lista de espera.", "Entre no grupo da lista de espera no WhatsApp para receber novidades, vídeos e o acesso à versão de teste em primeira mão.", "Entrar no grupo do WhatsApp"],
  en: ["The OptiMOB WhatsApp group is now open", "We created a group for the waitlist.", "Join the waitlist group on WhatsApp to get news, videos and beta access before anyone else.", "Join the WhatsApp group"],
  es: ["Ya está abierto el grupo de OptiMOB en WhatsApp", "Creamos un grupo para la lista de espera.", "Únete al grupo de la lista de espera en WhatsApp para recibir novedades, vídeos y el acceso a la versión de prueba antes que nadie.", "Unirme al grupo de WhatsApp"],
  fr: ["Le groupe WhatsApp d'OptiMOB est ouvert", "Nous avons créé un groupe pour la liste d'attente.", "Rejoignez le groupe de la liste d'attente sur WhatsApp pour recevoir les nouveautés, les vidéos et l'accès à la version de test en avant-première.", "Rejoindre le groupe WhatsApp"],
  ru: ["Группа OptiMOB в WhatsApp открыта", "Мы создали группу для списка ожидания.", "Присоединяйтесь к группе списка ожидания в WhatsApp, чтобы первыми получать новости, видео и доступ к тестовой версии.", "Вступить в группу WhatsApp"],
  ar: ["مجموعة OptiMOB على واتساب مفتوحة الآن", "أنشأنا مجموعة لقائمة الانتظار.", "انضم إلى مجموعة قائمة الانتظار على واتساب لتصلك الأخبار ومقاطع الفيديو والوصول إلى النسخة التجريبية قبل الجميع.", "الانضمام إلى مجموعة واتساب"],
  vi: ["Nhóm WhatsApp của OptiMOB đã mở", "Chúng tôi đã tạo một nhóm cho danh sách chờ.", "Tham gia nhóm danh sách chờ trên WhatsApp để nhận tin tức, video và quyền dùng thử sớm nhất.", "Tham gia nhóm WhatsApp"],
  zh: ["OptiMOB WhatsApp 群组已开放", "我们为候补名单建立了一个群组。", "加入 WhatsApp 候补名单群组，第一时间获取最新动态、视频和测试版使用资格。", "加入 WhatsApp 群组"],
  de: ["Die OptiMOB-WhatsApp-Gruppe ist jetzt offen", "Wir haben eine Gruppe für die Warteliste erstellt.", "Treten Sie der Wartelisten-Gruppe auf WhatsApp bei und erhalten Sie Neuigkeiten, Videos und Zugang zur Testversion als Erste.", "Der WhatsApp-Gruppe beitreten"],
  it: ["Il gruppo WhatsApp di OptiMOB è aperto", "Abbiamo creato un gruppo per la lista d'attesa.", "Unisciti al gruppo della lista d'attesa su WhatsApp per ricevere novità, video e l'accesso alla versione di prova in anteprima.", "Entra nel gruppo WhatsApp"],
  nl: ["De WhatsApp-groep van OptiMOB is open", "We hebben een groep gemaakt voor de wachtlijst.", "Word lid van de wachtlijstgroep op WhatsApp en ontvang als eerste nieuws, video's en toegang tot de testversie.", "Lid worden van de WhatsApp-groep"],
  pl: ["Grupa OptiMOB na WhatsAppie jest już otwarta", "Utworzyliśmy grupę dla listy oczekujących.", "Dołącz do grupy listy oczekujących na WhatsAppie, aby jako pierwszy otrzymywać nowości, filmy i dostęp do wersji testowej.", "Dołącz do grupy WhatsApp"],
  tr: ["OptiMOB WhatsApp grubu açıldı", "Bekleme listesi için bir grup oluşturduk.", "Haberleri, videoları ve test sürümüne erişimi herkesten önce almak için WhatsApp'taki bekleme listesi grubuna katılın.", "WhatsApp grubuna katıl"],
  el: ["Η ομάδα του OptiMOB στο WhatsApp άνοιξε", "Δημιουργήσαμε μια ομάδα για τη λίστα αναμονής.", "Μπείτε στην ομάδα της λίστας αναμονής στο WhatsApp για να λαμβάνετε πρώτοι νέα, βίντεο και πρόσβαση στη δοκιμαστική έκδοση.", "Είσοδος στην ομάδα WhatsApp"],
  uk: ["Група OptiMOB у WhatsApp відкрита", "Ми створили групу для списку очікування.", "Приєднуйтеся до групи списку очікування у WhatsApp, щоб першими отримувати новини, відео та доступ до тестової версії.", "Приєднатися до групи WhatsApp"],
  ro: ["Grupul OptiMOB pe WhatsApp este deschis", "Am creat un grup pentru lista de așteptare.", "Intră în grupul listei de așteptare pe WhatsApp pentru a primi primul noutăți, videoclipuri și acces la versiunea de test.", "Intră în grupul de WhatsApp"],
  cs: ["Skupina OptiMOB na WhatsAppu je otevřená", "Vytvořili jsme skupinu pro čekací listinu.", "Připojte se ke skupině čekací listiny na WhatsAppu a získejte jako první novinky, videa a přístup k testovací verzi.", "Připojit se ke skupině WhatsApp"],
  sk: ["Skupina OptiMOB na WhatsAppe je otvorená", "Vytvorili sme skupinu pre čakaciu listinu.", "Pridajte sa do skupiny čakacej listiny na WhatsAppe a získajte ako prví novinky, videá a prístup k testovacej verzii.", "Pridať sa do skupiny WhatsApp"],
  hu: ["Megnyílt az OptiMOB WhatsApp-csoportja", "Csoportot hoztunk létre a várólistának.", "Csatlakozzon a várólista WhatsApp-csoportjához, hogy elsőként kapja meg a híreket, videókat és a tesztverzióhoz való hozzáférést.", "Csatlakozás a WhatsApp-csoporthoz"],
  sv: ["OptiMOB:s WhatsApp-grupp är öppen", "Vi har skapat en grupp för väntelistan.", "Gå med i väntelistans grupp på WhatsApp och få nyheter, videor och tillgång till testversionen först av alla.", "Gå med i WhatsApp-gruppen"],
  da: ["OptiMOBs WhatsApp-gruppe er åben", "Vi har oprettet en gruppe til ventelisten.", "Bliv medlem af ventelistens gruppe på WhatsApp, og få nyheder, videoer og adgang til testversionen før alle andre.", "Bliv medlem af WhatsApp-gruppen"],
  nb: ["OptiMOBs WhatsApp-gruppe er åpen", "Vi har opprettet en gruppe for ventelisten.", "Bli med i ventelistegruppen på WhatsApp og få nyheter, videoer og tilgang til testversjonen før alle andre.", "Bli med i WhatsApp-gruppen"],
  fi: ["OptiMOBin WhatsApp-ryhmä on avattu", "Loimme ryhmän odotuslistalle.", "Liity odotuslistan WhatsApp-ryhmään ja saat uutiset, videot ja pääsyn testiversioon ensimmäisten joukossa.", "Liity WhatsApp-ryhmään"],
  mk: ["Групата на OptiMOB на WhatsApp е отворена", "Создадовме група за листата на чекање.", "Придружете се на групата на листата на чекање на WhatsApp и први добивајте новости, видеа и пристап до тест-верзијата.", "Придружи се на WhatsApp групата"],
  bg: ["Групата на OptiMOB в WhatsApp е отворена", "Създадохме група за списъка с чакащи.", "Присъединете се към групата на списъка с чакащи в WhatsApp, за да получавате първи новини, видеа и достъп до тестовата версия.", "Присъединяване към групата в WhatsApp"],
  sr: ["Група OptiMOB на WhatsApp-у је отворена", "Направили смо групу за листу чекања.", "Придружите се групи листе чекања на WhatsApp-у и први добијајте новости, видео-снимке и приступ тест-верзији.", "Придружи се WhatsApp групи"],
  hr: ["Grupa OptiMOB na WhatsAppu je otvorena", "Napravili smo grupu za listu čekanja.", "Pridružite se grupi liste čekanja na WhatsAppu i prvi primajte novosti, videozapise i pristup testnoj verziji.", "Pridruži se WhatsApp grupi"],
  he: ["קבוצת הוואטסאפ של OptiMOB פתוחה", "פתחנו קבוצה לרשימת ההמתנה.", "הצטרפו לקבוצת רשימת ההמתנה בוואטסאפ כדי לקבל ראשונים עדכונים, סרטונים וגישה לגרסת הניסיון.", "הצטרפות לקבוצת הוואטסאפ"],
  fa: ["گروه واتساپ OptiMOB باز شد", "برای فهرست انتظار یک گروه ساختیم.", "به گروه فهرست انتظار در واتساپ بپیوندید تا اخبار، ویدیوها و دسترسی به نسخهٔ آزمایشی را زودتر از همه دریافت کنید.", "پیوستن به گروه واتساپ"],
  ur: ["OptiMOB کا واٹس ایپ گروپ کھل گیا ہے", "ہم نے انتظار فہرست کے لیے ایک گروپ بنایا ہے۔", "واٹس ایپ پر انتظار فہرست کے گروپ میں شامل ہوں اور خبریں، ویڈیوز اور آزمائشی ورژن تک رسائی سب سے پہلے حاصل کریں۔", "واٹس ایپ گروپ میں شامل ہوں"],
  hi: ["OptiMOB का WhatsApp ग्रुप खुल गया है", "हमने प्रतीक्षा सूची के लिए एक ग्रुप बनाया है।", "WhatsApp पर प्रतीक्षा सूची ग्रुप से जुड़ें और सबसे पहले खबरें, वीडियो और टेस्ट संस्करण की पहुँच पाएँ।", "WhatsApp ग्रुप से जुड़ें"],
  bn: ["OptiMOB-এর WhatsApp গ্রুপ চালু হয়েছে", "অপেক্ষমাণ তালিকার জন্য আমরা একটি গ্রুপ তৈরি করেছি।", "WhatsApp-এ অপেক্ষমাণ তালিকার গ্রুপে যোগ দিন এবং সবার আগে খবর, ভিডিও ও পরীক্ষামূলক সংস্করণের অ্যাক্সেস পান।", "WhatsApp গ্রুপে যোগ দিন"],
  id: ["Grup WhatsApp OptiMOB sudah dibuka", "Kami membuat grup untuk daftar tunggu.", "Gabung ke grup daftar tunggu di WhatsApp untuk mendapatkan kabar terbaru, video, dan akses versi uji coba lebih dulu.", "Gabung ke grup WhatsApp"],
  ms: ["Kumpulan WhatsApp OptiMOB kini dibuka", "Kami telah mewujudkan kumpulan untuk senarai menunggu.", "Sertai kumpulan senarai menunggu di WhatsApp untuk mendapatkan berita, video dan akses versi percubaan lebih awal.", "Sertai kumpulan WhatsApp"],
  th: ["กลุ่ม WhatsApp ของ OptiMOB เปิดแล้ว", "เราสร้างกลุ่มสำหรับรายชื่อรอแล้ว", "เข้าร่วมกลุ่มรายชื่อรอใน WhatsApp เพื่อรับข่าวสาร วิดีโอ และสิทธิ์ใช้เวอร์ชันทดลองก่อนใคร", "เข้าร่วมกลุ่ม WhatsApp"],
  ja: ["OptiMOB の WhatsApp グループを開設しました", "ウェイティングリスト用のグループを作りました。", "WhatsApp のウェイティングリストグループに参加すると、最新情報や動画、テスト版へのアクセスをいち早くお届けします。", "WhatsApp グループに参加する"],
  ko: ["OptiMOB WhatsApp 그룹이 열렸습니다", "대기자 명단을 위한 그룹을 만들었습니다.", "WhatsApp 대기자 명단 그룹에 참여하시면 소식, 영상, 테스트 버전 이용 기회를 가장 먼저 받아 보실 수 있습니다.", "WhatsApp 그룹 참여하기"],
  sw: ["Kikundi cha WhatsApp cha OptiMOB kimefunguliwa", "Tumeunda kikundi kwa ajili ya orodha ya kusubiri.", "Jiunge na kikundi cha orodha ya kusubiri kwenye WhatsApp upate habari, video na ufikiaji wa toleo la majaribio kabla ya wengine.", "Jiunge na kikundi cha WhatsApp"],
  fil: ["Bukas na ang WhatsApp group ng OptiMOB", "Gumawa kami ng group para sa waitlist.", "Sumali sa waitlist group sa WhatsApp para mauna sa mga balita, video at access sa test version.", "Sumali sa WhatsApp group"],
};

function caixaGrupo(lang: string, dir: string) {
  const w = W[lang] ?? W.en;
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:6px 0 20px;background:#111313;border:1px solid #2A2F30;border-${dir === "rtl" ? "right" : "left"}:4px solid #25D366"><tr><td dir="${dir}" style="padding:18px 20px;text-align:${dir === "rtl" ? "right" : "left"}">
      <p style="font-size:14px;line-height:1.6;color:#C9CDCB;margin:0 0 14px">${esc(w[2])}</p>
      <a href="${WA_URL}" style="display:inline-block;background:#25D366;color:#0B1F12;font-weight:700;font-size:14px;text-decoration:none;padding:12px 18px">${esc(w[3])} →</a>
    </td></tr></table>`;
}

function bloco(t: T, lang: string, dir: string, email: string, perfil: string, tag: string, cta: boolean) {
  const p2 = esc(t.p2).replace("{e}", `<b style="color:#EEF0EA">${esc(email)}</b>`).replace("{p}", esc(perfilEm(t, perfil)));
  return `<div ${LABEL}>${esc(t.label)}${tag}</div>
    <h1 style="font-size:24px;line-height:1.3;margin:12px 0 14px;font-weight:700">${esc(t.h1)}</h1>
    <p ${P}>${esc(t.p1)}</p>
    <p ${P}>${p2}</p>
    ${caixaGrupo(lang, dir)}
    <p style="font-size:15px;line-height:1.6;color:#C9CDCB;margin:0 0 ${cta ? 24 : 14}px">${esc(t.p3)}</p>` +
    (cta ? `<a href="https://optimobsystem.com" style="display:inline-block;background:#3AA0FF;color:#1B1E1E;font-weight:700;font-size:14px;text-decoration:none;padding:12px 18px">optimobsystem.com</a>` : "");
}

// Corpo de um bloco do convite para o grupo (para quem se inscreveu antes de o grupo existir).
function blocoConvite(t: T, lang: string, dir: string, tag: string, cta: boolean) {
  const w = W[lang] ?? W.en;
  return `<div ${LABEL}>${esc(t.label)}${tag}</div>
    <h1 style="font-size:24px;line-height:1.3;margin:12px 0 14px;font-weight:700">${esc(w[1])}</h1>
    ${caixaGrupo(lang, dir)}
    <p style="font-size:15px;line-height:1.6;color:#C9CDCB;margin:0 0 ${cta ? 24 : 14}px">${esc(t.p3)}</p>` +
    (cta ? `<a href="https://optimobsystem.com" style="display:inline-block;background:#3AA0FF;color:#1B1E1E;font-weight:700;font-size:14px;text-decoration:none;padding:12px 18px">optimobsystem.com</a>` : "");
}

type Tipo = "confirmacao" | "convite";

function html(email: string, perfil: string, lang: string | null, tipo: Tipo = "confirmacao") {
  const codes = lang ? [lang] : ["pt", "en"];
  const dir = lang && RTL.has(lang) ? "rtl" : "ltr";
  const corpo = codes.map((c, i) => {
    const t = L[c], tag = lang ? "" : (i ? " · EN" : " · PT"), last = i === codes.length - 1;
    const inner = tipo === "convite" ? blocoConvite(t, c, dir, tag, last) : bloco(t, c, dir, email, perfil, tag, last);
    return `<tr><td dir="${dir}" style="padding:${i ? 24 : 28}px 36px 8px;color:#EEF0EA;text-align:${dir === "rtl" ? "right" : "left"}">${inner}</td></tr>`;
  }).join(`<tr><td style="padding:8px 36px 0"><div style="height:1px;background:#2A2F30"></div></td></tr>`);
  const corpoFinal = dir === "rtl" ? corpo.replace(/letter-spacing:3px;/g, "") : corpo; // espaçamento parte a escrita árabe
  const pe = codes.map((c, i) => `<p dir="${dir}" style="font-size:12px;line-height:1.6;color:#8A918F;margin:0 0 ${i < codes.length - 1 ? 6 : 0}px;text-align:${dir === "rtl" ? "right" : "left"}">${esc(L[c].foot)}</p>`).join("");
  return `<!doctype html><html lang="${lang ?? "pt"}" dir="${dir}"><body style="margin:0;background:#111313;padding:32px 16px;font-family:Helvetica,Arial,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#1B1E1E;border:1px solid #2A2F30">
  <tr><td style="padding:36px 36px 8px" dir="ltr">
    <div style="font-size:28px;letter-spacing:-0.5px;color:#EEF0EA">Opti<b style="color:#3AA0FF">MOB</b></div>
    <div style="width:120px;height:3px;background:#3AA0FF;margin:10px 0 0"></div>
  </td></tr>
  ${corpoFinal}
  <tr><td style="padding:32px 36px 28px;border-top:1px solid #2A2F30">${pe}</td></tr>
</table></td></tr></table></body></html>`;
}

function text(email: string, perfil: string, lang: string | null, tipo: Tipo = "confirmacao") {
  const codes = lang ? [lang] : ["pt", "en"];
  return codes.map((c) => {
    const t = L[c], w = W[c] ?? W.en;
    const grupo = `${w[2]}\n${w[3]}: ${WA_URL}`;
    return tipo === "convite" ? `${w[1]}\n\n${grupo}\n\n${t.p3}`
      : `${t.h1}\n\n${t.p1}\n${t.p2.replace("{e}", email).replace("{p}", perfilEm(t, perfil))}\n\n${grupo}\n\n${t.p3}`;
  }).join("\n\n---\n\n") + "\n\nhttps://optimobsystem.com\n\n" + codes.map((c) => L[c].foot).join("\n");
}

function assunto(lang: string | null, tipo: Tipo = "confirmacao") {
  const a = (c: string) => tipo === "convite" ? (W[c] ?? W.en)[0] : L[c].subject;
  return lang ? a(lang) : `${a("pt")} · ${a("en")}`;
}

// Corre em segundo plano depois de responder ao webhook (Supabase Edge Runtime).
declare const EdgeRuntime: { waitUntil(p: Promise<unknown>): void } | undefined;

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const TENTATIVAS = 5;

// Envia com repetição: se a Resend responder 429 (demasiados pedidos) ou 5xx, espera e tenta outra vez.
// O Idempotency-Key garante que uma repetição nunca gera um segundo email para a mesma inscrição.
async function enviar(rec: { id?: string; email: string; perfil?: string; idioma?: string | null }, tipo: Tipo = "confirmacao") {
  const lang = lingua(rec.idioma);
  const body = JSON.stringify({
    from: FROM,
    to: [rec.email],
    reply_to: REPLY_TO,
    subject: assunto(lang, tipo),
    html: html(rec.email, rec.perfil ?? "", lang, tipo),
    text: text(rec.email, rec.perfil ?? "", lang, tipo),
  });
  const chave = `${tipo === "convite" ? "convite-grupo" : "lista-espera"}-${rec.id ?? rec.email}`;

  for (let tentativa = 1; tentativa <= TENTATIVAS; tentativa++) {
    let estado = 0, detalhe = "";
    try {
      const r = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
          "Idempotency-Key": chave,
        },
        body,
      });
      if (r.ok) {
        console.log("Enviado", tipo, rec.email, lang ?? "pt+en", "tentativa", tentativa);
        return true;
      }
      estado = r.status;
      detalhe = await r.text();
      const repetir = estado === 429 || estado >= 500;
      if (!repetir) {
        console.error("Resend recusou", estado, detalhe);
        return false;
      }
      const ra = Number(r.headers.get("retry-after"));
      await sleep(ra > 0 ? ra * 1000 : 600 * 2 ** (tentativa - 1) + Math.random() * 300);
    } catch (err) {
      detalhe = String(err);
      await sleep(600 * 2 ** (tentativa - 1));
    }
    console.warn("Nova tentativa", tentativa, rec.email, estado, detalhe.slice(0, 200));
  }
  console.error("Falhou após", TENTATIVAS, "tentativas:", rec.email);
  return false;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });
  if (!WEBHOOK_SECRET || req.headers.get("x-webhook-secret") !== WEBHOOK_SECRET) {
    return new Response("Unauthorized", { status: 401 });
  }
  if (!RESEND_API_KEY) return new Response("RESEND_API_KEY em falta", { status: 500 });

  const payload = await req.json().catch(() => null);
  const rec = payload?.record;
  // "INSERT": inscrição nova (webhook). "CONVITE_GRUPO": convite para o grupo do WhatsApp,
  // enviado à mão (SQL) a quem se inscreveu antes de o grupo existir.
  const tipo: Tipo | null = payload?.type === "INSERT" ? "confirmacao" : payload?.type === "CONVITE_GRUPO" ? "convite" : null;
  if (!tipo || payload?.table !== "lista_espera" || !rec?.email) {
    return new Response("Ignorado", { status: 200 });
  }

  const tarefa = enviar(rec, tipo);
  if (typeof EdgeRuntime !== "undefined" && EdgeRuntime?.waitUntil) {
    EdgeRuntime.waitUntil(tarefa);
    return new Response("Aceite", { status: 202 });
  }
  const ok = await tarefa;
  return new Response(ok ? "Enviado" : "Falha no envio", { status: ok ? 200 : 502 });
});
