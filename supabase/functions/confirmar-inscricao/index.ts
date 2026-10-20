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

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const WEBHOOK_SECRET = Deno.env.get("WEBHOOK_SECRET") ?? "";
const FROM = Deno.env.get("EMAIL_FROM") ?? "OptiMOB <ola@optimobsystem.com>";
const REPLY_TO = Deno.env.get("EMAIL_REPLY_TO") ?? "optimobsystem@gmail.com";

const esc = (s: string) =>
  s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));

const PERFIL_EN: Record<string, string> = {
  "Marcenaria": "Joinery / woodworking shop",
  "Designer de interiores": "Interior designer",
  "Fábrica de mobiliário": "Furniture factory",
  "Outro": "Other",
};

const P = 'style="font-size:15px;line-height:1.6;color:#C9CDCB;margin:0 0 14px"';
const LABEL = 'style="font-family:Courier New,monospace;font-size:11px;letter-spacing:3px;color:#3AA0FF;text-transform:uppercase"';

function html(email: string, perfil: string) {
  const e = esc(email), pt = esc(perfil), en = esc(PERFIL_EN[perfil] ?? perfil);
  return `<!doctype html><html lang="pt"><body style="margin:0;background:#111313;padding:32px 16px;font-family:Helvetica,Arial,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#1B1E1E;border:1px solid #2A2F30">
  <tr><td style="padding:36px 36px 8px">
    <div style="font-size:28px;letter-spacing:-0.5px;color:#EEF0EA">Opti<b style="color:#3AA0FF">MOB</b></div>
    <div style="width:120px;height:3px;background:#3AA0FF;margin:10px 0 0"></div>
  </td></tr>
  <tr><td style="padding:28px 36px 4px;color:#EEF0EA">
    <div ${LABEL}>Acesso antecipado · PT</div>
    <h1 style="font-size:24px;line-height:1.2;margin:12px 0 14px;font-weight:700">Está na lista de espera.</h1>
    <p ${P}>Obrigado pelo interesse no OptiMOB, a extensão de blocos paramétricos de marcenaria para SketchUp.</p>
    <p ${P}>Registámos <b style="color:#EEF0EA">${e}</b> (${pt}). Quando a versão de teste estiver pronta, enviamos-lhe as instruções de instalação para este email.</p>
    <p ${P}>Tem alguma pergunta? Basta responder a este email.</p>
  </td></tr>
  <tr><td style="padding:8px 36px 0"><div style="height:1px;background:#2A2F30"></div></td></tr>
  <tr><td style="padding:24px 36px 8px;color:#EEF0EA">
    <div ${LABEL}>Early access · EN</div>
    <h1 style="font-size:24px;line-height:1.2;margin:12px 0 14px;font-weight:700">You're on the waitlist.</h1>
    <p ${P}>Thank you for your interest in OptiMOB, the parametric joinery blocks extension for SketchUp.</p>
    <p ${P}>We registered <b style="color:#EEF0EA">${e}</b> (${en}). When the beta is ready, we will send the installation instructions to this address.</p>
    <p style="font-size:15px;line-height:1.6;color:#C9CDCB;margin:0 0 24px">Any questions? Just reply to this email.</p>
    <a href="https://optimobsystem.com" style="display:inline-block;background:#3AA0FF;color:#1B1E1E;font-weight:700;font-size:14px;text-decoration:none;padding:12px 18px">optimobsystem.com →</a>
  </td></tr>
  <tr><td style="padding:32px 36px 28px;border-top:1px solid #2A2F30">
    <p style="font-size:12px;line-height:1.6;color:#8A918F;margin:0 0 6px">Recebeu este email porque se inscreveu na lista de acesso antecipado em optimobsystem.com. Para sair da lista e apagar os seus dados, responda com "remover".</p>
    <p style="font-size:12px;line-height:1.6;color:#8A918F;margin:0">You received this email because you joined the early access list at optimobsystem.com. To leave the list and delete your data, reply with "remove".</p>
  </td></tr>
</table></td></tr></table></body></html>`;
}

function text(email: string, perfil: string) {
  const en = PERFIL_EN[perfil] ?? perfil;
  return `[PT] Está na lista de espera do OptiMOB.

Obrigado pelo interesse no OptiMOB, a extensão de blocos paramétricos de marcenaria para SketchUp.
Registámos ${email} (${perfil}). Quando a versão de teste estiver pronta, enviamos-lhe as instruções de instalação para este email.
Tem alguma pergunta? Basta responder a este email.

[EN] You're on the OptiMOB waitlist.

Thank you for your interest in OptiMOB, the parametric joinery blocks extension for SketchUp.
We registered ${email} (${en}). When the beta is ready, we will send the installation instructions to this address.
Any questions? Just reply to this email.

https://optimobsystem.com

Para sair da lista, responda "remover". / To leave the list, reply "remove".`;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });
  if (!WEBHOOK_SECRET || req.headers.get("x-webhook-secret") !== WEBHOOK_SECRET) {
    return new Response("Unauthorized", { status: 401 });
  }
  if (!RESEND_API_KEY) return new Response("RESEND_API_KEY em falta", { status: 500 });

  const payload = await req.json().catch(() => null);
  const rec = payload?.record;
  if (payload?.type !== "INSERT" || payload?.table !== "lista_espera" || !rec?.email) {
    return new Response("Ignorado", { status: 200 });
  }

  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: FROM,
      to: [rec.email],
      reply_to: REPLY_TO,
      subject: "Está na lista de espera do OptiMOB · You're on the OptiMOB waitlist",
      html: html(rec.email, rec.perfil ?? ""),
      text: text(rec.email, rec.perfil ?? ""),
    }),
  });

  if (!r.ok) {
    console.error("Resend", r.status, await r.text());
    return new Response("Falha no envio", { status: 502 });
  }
  return new Response("Enviado", { status: 200 });
});
