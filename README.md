# ⚖️ Jul.IA DataJud – Monitor Inteligente de Processos

A **Jul.IA DataJud** é o módulo da Jul.IA focado em **pesquisa, consolidação e monitoramento automático de processos judiciais**, começando pela API do **JusBrasil** e preparado para, depois, plugar diretamente nas APIs dos tribunais (DataJud/TJs).

Pensado para uso diário em escritório, ela permite que você consulte e acompanhe processos pelo **CPF/CNPJ, número CNJ ou nome da parte**, integrando tudo com:

- 🧠 a Jul.IA (camada de IA/assistente),
- 💬 a Secretária Virtual do WhatsApp,
- 🌐 e um backend em FastAPI pronto para crescer.

---

## 🚀 Principais funcionalidades

- 🔍 **Consulta instantânea de processos**
  - Busca por **número CNJ**, **CPF/CNPJ** ou **nome da parte**.
  - Normalização dos dados (tribunal, classe, assunto, fase, movimento mais recente).

- 📡 **Monitoramento automático**
  - Registro de processos para acompanhamento contínuo.
  - Checagens periódicas na fonte (JusBrasil / DataJud / API do tribunal).
  - Geração de “eventos de atualização” para a Jul.IA (ex.: novo andamento relevante).

- 📲 **Integração com WhatsApp (Jul.IA Secretária)**
  - Comandos tipo:
    - `/processo 0000000-00.0000.0.00.0000`
    - `/monitorar 0000000-00.0000.0.00.0000`
    - `/andamentos 0000000-00.0000.0.00.0000`
  - Respostas em linguagem natural, prontas pra copiar/colar para o cliente.

- 🗂 **Histórico consolidado**
  - Guarda consultas e monitoramentos por **cliente**, **processo** e **origem da API**.
  - Facilita relatórios, painéis e dashboards posteriores.

- 🧩 **Arquitetura extensível**
  - Camada de “fonte de dados” desacoplada:
    - hoje: JusBrasil,
    - depois: TJPR, TJSP, TJMG, CNJ/DataJud, etc.
  - Permite trocar a origem dos dados sem alterar o fluxo do bot.

---

## 🧱 Arquitetura em alto nível

```text
WhatsApp (Meta API / Manus)
        ↓
Jul.IA Secretária Virtual (fluxos / comandos)
        ↓ HTTP
Backend Jul.IA DataJud (FastAPI)
        ↓
Módulo jusbrasil_client.py  →  Futuras integrações (TJPR, TJSP, TJMG, DataJud)
        ↓
Banco de dados / cache (consultas, monitoramentos, histórico)
