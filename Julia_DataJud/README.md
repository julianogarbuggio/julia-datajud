# Jul.IA – Integração DataJud + Jusbrasil (API para Manus / WhatsApp)

Este pacote contém uma API FastAPI que integra:

- **DataJud (CNJ)** – consulta processual pública, gratuita.
- **Jusbrasil** – consulta processual por CPF/CNPJ e por CNJ (para quem tem API contratada).

A API é pensada para ser usada pela **Júlia (WhatsApp)** rodando no Manus, e também
para deploy em Railway / GitHub.

## Endpoints principais

- `/api/datajud/consulta-processo` (POST)
- `/api/datajud/consulta-processo-auto` (POST)
- `/api/jusbrasil/consulta-cpf` (POST)
- `/api/jusbrasil/consulta-cnj` (POST)

Veja o código para detalhes de payload e resposta.
