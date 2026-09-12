# RAG MCP Omie VerticalParts — SPEC + SDD + Retrieval + Fine-Tuning Ready

> Documento canônico para qualquer LLM, agente ou automação que precise entender e usar corretamente o MCP Omie da VerticalParts.
>
> Escopo: Omie ERP, MCP Omie, documentação oficial do Omie, espelho Supabase e regras de negócio Omie documentadas neste repositório.

---

## 0. Regra de ouro para a LLM

Quando a solicitação envolver Omie, ERP, cliente, fornecedor, produto, estoque, financeiro, compra, venda, serviço, NF-e, NFS-e, CRM, pedido, título, boleto, PIX, DRE, projeto, departamento, categoria financeira ou qualquer entidade descrita na API Omie:

1. identifique a intenção de negócio;
2. classifique o módulo Omie envolvido;
3. consulte este RAG para semântica, regras, gaps e roteamento;
4. use o MCP Omie para dados vivos e operações quando houver tool compatível;
5. use o espelho Supabase para análise histórica e cruzamentos quando apropriado e autorizado;
6. nunca invente tool, endpoint, campo, código Omie, valor, status ou resultado;
7. antes de qualquer escrita, valide entidade, identificador, campos críticos e impacto;
8. em caso de dúvida entre documentação e dado vivo, preserve a distinção entre as fontes.

Endpoint corporativo do MCP Omie:

`https://mcp.vpsistema.com/omie/mcp`

Nunca grave credenciais, app_key, app_secret, tokens ou senhas neste repositório.

---

# PARTE I — IDENTIDADE E FONTES DE VERDADE

## 1. Objetivo deste RAG

Este documento é a camada de conhecimento e decisão do MCP Omie. Ele serve para ensinar uma LLM a:

- interpretar pedidos em linguagem natural;
- mapear cada pedido ao módulo Omie correto;
- escolher entre MCP, documentação e espelho analítico;
- descobrir e usar somente tools realmente disponíveis;
- tratar paginação, filtros, identificadores, datas e ambiguidades;
- reconhecer gaps documentados;
- evitar alucinações;
- operar escrita de forma segura e verificável;
- produzir respostas curtas quando possível e detalhadas quando necessário;
- agir de forma consistente entre Claude, ChatGPT, Codex ou outro agente compatível com MCP.

Este RAG combina quatro funções:

- RAG: recuperação estruturada de conhecimento;
- SPEC: requisitos funcionais e comportamentais;
- SDD: desenho técnico e fluxo de decisão;
- Fine-Tuning Ready: exemplos canônicos, anti-exemplos e critérios de avaliação.

## 2. O que este documento não substitui

Este RAG não substitui:

- a API Omie;
- o servidor MCP;
- a documentação oficial do Omie;
- o estado atual dos dados operacionais;
- autorizações humanas para operações sensíveis;
- controles de segurança da infraestrutura.

Documentação explica. MCP consulta e opera. Espelho analisa.

## 3. Hierarquia de fontes

Quando houver conflito, seguir esta ordem:

1. resposta atual do MCP Omie / API Omie para estado operacional vivo;
2. documentação oficial Omie para contrato de endpoint, parâmetros e semântica oficial;
3. este RAG para política de uso, roteamento, segurança, comportamento e gaps consolidados;
4. `instructions.md` como índice de consumo do repositório;
5. `README.md` como catálogo do espelho Omie ↔ Supabase;
6. issues #1 a #9 como mapeamento detalhado por módulo;
7. espelho Supabase para análise histórica, cruzamentos e grandes volumes, respeitando sua defasagem de sincronização.

Nunca apresentar dado documental como se fosse estado vivo do Omie.

---

# PARTE II — SPEC: ESPECIFICAÇÃO COMPORTAMENTAL

## 4. FR-001 — Descoberta de tools

Antes de executar qualquer operação, a LLM deve observar as tools realmente expostas pelo MCP da sessão.

Regras:

- não inventar nome de tool;
- não presumir que uma capability existe por semelhança com a API;
- preferir a tool mais específica para a tarefa;
- ler o schema de entrada antes de montar argumentos;
- se a tool necessária não existir, dizer isso claramente.

## 5. FR-002 — Classificação por domínio

Toda solicitação deve ser classificada em um ou mais módulos:

- Geral / Cadastros;
- CRM;
- Finanças;
- Compras;
- Impostos;
- Estoque;
- Vendas e NF-e;
- Serviços e NFS-e;
- Painel do Contador.

Uma pergunta pode atravessar módulos. Exemplo: “qual pedido de compra gerou esta nota de entrada?” envolve Compras e documentos de entrada.

## 6. FR-003 — Seleção da fonte

Use MCP Omie quando o usuário pedir:

- estado atual;
- consulta operacional;
- localização de cliente, fornecedor, produto, pedido, título, OS ou oportunidade;
- criação, alteração, exclusão, cancelamento ou outra mutação;
- informação cujo frescor seja relevante.

Use RAG/documentação quando o usuário pedir:

- qual módulo representa uma entidade;
- qual tabela espelha determinado dado;
- qual endpoint existe;
- quais campos ou regras são conhecidos;
- quais gaps estão documentados;
- como estruturar uma integração.

Use espelho Supabase quando disponível e apropriado para:

- séries históricas;
- grandes agregações;
- cruzamentos entre muitas entidades;
- dashboards;
- análises que seriam ineficientes via paginação da API.

## 7. FR-004 — Identificadores

Nunca assumir que nome textual é identificador único.

Preferir identificadores estáveis, conforme a entidade:

- `codigo_cliente_omie`;
- código do produto;
- código do pedido;
- código do título;
- código da OS;
- código de oportunidade;
- identificadores específicos retornados pela API.

Quando houver múltiplos candidatos:

1. mostrar opções relevantes;
2. incluir dados suficientes para distinção;
3. solicitar desambiguação apenas se necessário.

## 8. FR-005 — Paginação

A API Omie usa paginação em diversas listagens.

Regras:

- a primeira página nunca deve ser tratada automaticamente como universo completo;
- se o usuário pedir “todos”, percorrer todas as páginas necessárias ou declarar limite técnico;
- se o usuário pedir amostra ou top N, buscar somente o necessário;
- para resumos, declarar cobertura e filtros;
- quando apropriado, deduplicar por identificador estável.

## 9. FR-006 — Datas e períodos

Toda consulta temporal deve explicitar:

- data inicial;
- data final;
- campo temporal utilizado quando houver mais de uma possibilidade;
- fuso horário quando afetar a interpretação.

Expressões como “hoje”, “esta semana” e “mês passado” devem ser resolvidas para datas concretas antes da consulta quando isso alterar o resultado operacional.

## 10. FR-007 — Escrita segura

Antes de alterar dados no Omie:

1. identificar a entidade correta;
2. resolver o registro alvo de forma inequívoca;
3. validar campos obrigatórios;
4. validar valores críticos;
5. explicar o efeito da operação quando houver risco de ambiguidade;
6. pedir confirmação quando a intenção não estiver inequívoca;
7. executar uma única mutação;
8. verificar o retorno;
9. relatar o identificador do registro afetado quando disponível.

Operações financeiras, fiscais, exclusões, cancelamentos e ações irreversíveis exigem cuidado adicional.

## 11. FR-008 — Idempotência e timeout

Timeout de transporte não significa que a operação falhou no Omie.

Em escrita:

- nunca repetir imediatamente a mesma mutação após timeout;
- primeiro consultar o estado final;
- só repetir se houver evidência de que a operação não ocorreu;
- evitar duplicidade de cadastro, lançamento, pedido ou título.

## 12. FR-009 — Gaps conhecidos

Se a solicitação cair em uma lacuna documentada, a LLM deve:

1. declarar o gap;
2. explicar o que está coberto;
3. apontar a alternativa disponível;
4. não inventar resultado para preencher a ausência.

## 13. FR-010 — Evidência

A resposta deve distinguir claramente:

- retorno do MCP;
- conhecimento documental;
- informação do espelho Supabase;
- inferência;
- recomendação.

## 14. FR-011 — Segurança de segredos

Nunca mostrar ou persistir em resposta:

- app_key;
- app_secret;
- tokens;
- senhas;
- cabeçalhos privados;
- chaves de serviço.

## 15. FR-012 — Economia de tokens

Recupere somente o necessário:

- uma issue específica em vez de todas;
- um módulo por vez quando possível;
- apenas campos envolvidos na tarefa;
- apenas exemplos pertinentes ao caso atual.

O objetivo é economizar contexto sem perder precisão.

---

# PARTE III — SDD: DESENHO E FLUXO DE DECISÃO

## 16. Arquitetura conceitual

```text
Usuário
  |
  v
LLM / Agente
  |-- interpreta intenção
  |-- consulta RAG para semântica e regras
  |-- descobre tools reais da sessão
  v
MCP Omie VerticalParts
  |
  v
API Omie / dados operacionais

Quando apropriado:
LLM -> espelho Supabase -> análise histórica e cruzamentos
```

## 17. Componentes

### A. LLM / Agente

Responsável por:

- compreender linguagem natural;
- classificar domínio;
- recuperar contexto;
- selecionar tool;
- validar argumentos;
- analisar resposta;
- comunicar resultado.

### B. RAG Omie

Responsável por:

- semântica de negócio;
- mapeamento de módulos;
- política de segurança;
- regras de paginação;
- gaps conhecidos;
- padrões de resposta;
- exemplos de comportamento.

### C. MCP Omie

Responsável por:

- expor tools;
- receber chamadas estruturadas;
- consultar ou operar o Omie;
- retornar dados estruturados.

### D. Omie ERP

Fonte operacional para o estado vivo das entidades.

### E. Espelho Supabase

Fonte auxiliar para análise e histórico. Nunca presumir sincronização instantânea sem evidência.

## 18. Fluxo de leitura

```text
1. interpretar pergunta
2. classificar módulo
3. resolver entidade e filtros
4. selecionar tool real
5. executar consulta
6. validar resposta
7. paginar se necessário
8. consolidar sem duplicidade
9. responder com conclusão, filtros e fonte
```

## 19. Fluxo de escrita

```text
1. interpretar intenção de alteração
2. identificar risco
3. localizar registro alvo
4. validar campos críticos
5. confirmar quando necessário
6. executar exatamente uma mutação
7. verificar retorno/estado final
8. relatar resultado e identificador
9. em timeout, consultar antes de repetir
```

## 20. Fluxo de recuperação RAG

```text
intent = classificar(pergunta)
modulo = mapear(intent)

ler RAG
se precisar de catálogo geral:
    consultar README.md
se precisar de regra, endpoint ou gap específico:
    consultar issue do módulo (#1..#9)
se contrato oficial estiver em dúvida:
    consultar documentação oficial Omie
se estado vivo for necessário:
    usar MCP Omie
se análise histórica de alto volume for necessária:
    usar espelho Supabase quando autorizado
```

---

# PARTE IV — MAPA DE CONHECIMENTO POR MÓDULO

## 21. Geral / Cadastros — Issue #1

Principais entidades documentadas:

- clientes;
- clientes_caract;
- cliente_tags;
- projetos;
- empresas;
- departamentos;
- categorias;
- parcelas;
- tipos_atividade;
- cidades;
- paises;
- tipos_anexo;
- anexos;
- tipos_entrega;
- tipos_assinante;
- tarefas_geral.

Uso típico:

- localizar cliente ou fornecedor;
- validar cadastro;
- resolver código Omie;
- localizar projeto, departamento ou categoria;
- preparar identificadores para módulos financeiro, compras e vendas.

Gap documentado: `Características de Produtos` (`/geral/caracteristicas/`).

## 22. CRM — Issue #2

Principais entidades:

- crm_contas;
- crm_contas_caract;
- crm_contatos;
- crm_oportunidades;
- crm_oportunidades_resumo;
- crm_tarefas;
- crm_tarefas_resumo;
- crm_solucoes;
- crm_fases;
- crm_usuarios;
- crm_status;
- crm_motivos;
- crm_tipos;
- crm_parceiros;
- crm_origens;
- crm_concorrentes;
- crm_verticais;
- crm_tipos_tarefa.

Uso típico:

- oportunidades;
- pipeline;
- contas e contatos;
- fases e status;
- tarefas comerciais;
- motivos de perda.

Gap documentado: `Finders`.

## 23. Finanças — Issue #3

Principais entidades:

- contas_correntes;
- contas_correntes_lancamentos;
- contas_pagar;
- contas_receber;
- contas_receber_boletos;
- pix;
- extrato;
- orcamento_caixa;
- titulos_pesquisa;
- movimentos_financeiros;
- bancos;
- tipos_documento;
- tipos_conta_corrente;
- contas_dre;
- finalidade_transferencia;
- origem_lancamento;
- bandeiras_cartao.

Uso típico:

- títulos a pagar e receber;
- vencidos e a vencer;
- fluxo de caixa;
- extrato;
- boleto e PIX;
- classificação financeira.

Gap documentado: endpoint agregado `Resumo`.

## 24. Compras — Issue #4

Principais entidades:

- produtos_variacao;
- produtos_lote;
- requisicoes_compra;
- pedidos_compra;
- ordens_producao;
- notas_entrada;
- notas_entrada_fat;
- recebimento_nfe;
- compradores;
- produto_fornecedor;
- formas_pagamento_compras;
- ncm.

Fluxo de compra recebida:

`pedidos_compra` + `notas_entrada` + `notas_entrada_fat` + `recebimento_nfe`.

O Omie não modela nativamente todas as fases logísticas de importação. Não inferir embarque, trânsito ou desembaraço a partir do simples status do pedido.

Gap documentado: `Resumo de Compras`.

## 25. Impostos — Issue #5

Principais entidades auxiliares:

- cfop;
- cnae;
- icms_cst;
- icms_csosn;
- icms_origem;
- pis_cst;
- cofins_cst;
- ipi_cst;
- ipi_enquadramento;
- tipo_calculo;
- cest;
- ncm.

Cobertura documental registrada: módulo considerado completo no mapeamento atual.

Regra: não inferir CFOP, CST, NCM ou enquadramento fiscal sem fonte adequada.

## 26. Estoque — Issue #6

Entidades:

- ajustes_estoque;
- consulta_estoque;
- movimento_estoque;
- locais_estoque.

Uso típico:

- saldo;
- posição por local;
- movimentação;
- ajustes.

Gap documentado: `Resumo do Estoque` agregado.

## 27. Vendas e NF-e — Issue #7

Entidades cobertas:

- pedidos_venda;
- pedidos_venda_resumo;
- pedidos_venda_fat;
- pedidos_venda_etapas;
- cte;
- remessa_produtos;
- remessa_fat;
- vendedores;
- formas_pagamento_vendas;
- tabela_precos;
- etapas_faturamento;
- meios_pagamento;
- origem_pedido;
- motivos_devolucao.

Gaps documentados:

- Resumo de Vendas;
- DFe / obtenção de documentos;
- Cupom Fiscal;
- NFC-e;
- SAT;
- consultas NF-e;
- utilitários NF-e;
- importar NF-e.

A capacidade real do MCP deve ser descoberta na sessão. Um gap documental não prova ausência de tool atual; uma tool atual também não apaga automaticamente um gap do espelho documentado.

## 28. Serviços e NFS-e — Issue #8

Entidades:

- servicos;
- ordens_servico;
- ordens_servico_fat;
- ordens_servico_lote;
- contratos_servico;
- contratos_fat;
- contratos_lote;
- servicos_municipio;
- tipos_tributacao;
- lc116;
- nbs;
- ibpt;
- contrato_tipo_fat;
- tipo_utilizacao;
- classificacao_servico.

Gaps documentados:

- Resumo de Serviços;
- documentos de OS;
- consultas NFS-e.

## 29. Painel do Contador — Issue #9

Entidade principal:

- documentos_fiscais_xml.

Gap documentado: resumo agregado do contador.

---

# PARTE V — ROTEADOR DE INTENÇÃO

## 30. Intenção → módulo → primeiro movimento

| Intenção | Módulo principal | Primeiro movimento |
|---|---|---|
| achar cliente/fornecedor | Geral | localizar cadastro e resolver código Omie |
| achar produto | Geral/Estoque | localizar produto antes de consultar saldo |
| estoque disponível | Estoque | consultar posição atual e local quando aplicável |
| conta vencida/a vencer | Finanças | filtrar títulos por situação e período |
| boleto/PIX | Finanças | localizar título e cobrança associada |
| pedido de compra | Compras | localizar pedido e verificar status/recebimento |
| mercadoria recebida | Compras/Estoque | cruzar pedido, nota de entrada e recebimento |
| pedido de venda | Vendas | localizar pedido, etapas e faturamento |
| oportunidade | CRM | localizar oportunidade, fase, status e conta |
| ordem de serviço | Serviços | localizar OS e situação/faturamento |
| contrato de serviço | Serviços | localizar contrato e faturamento |
| NF-e/NFS-e | Vendas/Serviços | descobrir capability real e considerar gaps documentados |
| CFOP/CST/NCM | Impostos | usar cadastro fiscal oficial, sem inferência |

## 31. Desambiguação

Perguntar quando faltar informação que mude materialmente a consulta, por exemplo:

- razão social com múltiplos cadastros;
- produto com descrição semelhante;
- período não definido;
- empresa ou filial não definida;
- “pedido” sem contexto suficiente para distinguir compra de venda;
- “nota” sem contexto suficiente para distinguir tipo de documento;
- escrita sem registro alvo inequívoco.

Não faça pergunta desnecessária quando a própria busca puder retornar opções seguras para escolha.

---

# PARTE VI — POLÍTICA DE USO DAS TOOLS

## 32. Nunca inventar tool

O MCP pode evoluir. Este RAG não congela uma lista eterna de nomes.

Procedimento:

1. observar tools da sessão;
2. escolher a mais específica;
3. conferir schema de entrada;
4. montar argumentos;
5. executar;
6. validar saída.

## 33. Preferência por tool específica

Se existir uma tool específica para uma entidade ou operação, prefira-a a uma chamada genérica.

Benefícios:

- menor chance de endpoint incorreto;
- parâmetros padronizados;
- melhor auditabilidade;
- menor exposição de detalhes internos;
- resposta mais consistente.

## 34. Paginação adaptativa

- “me dê 10” → buscar o necessário;
- “todos” → paginar até o fim;
- “resuma” → buscar volume suficiente e declarar cobertura;
- grandes volumes históricos → considerar o espelho analítico quando autorizado.

## 35. Deduplicação

Quando houver repetição de registros:

- deduplicar por identificador Omie estável;
- nunca deduplicar somente por descrição, data ou valor;
- IDs distintos significam registros distintos até prova em contrário.

---

# PARTE VII — CONTRATO DE RESPOSTA

## 36. Consulta simples

Formato recomendado:

1. resposta direta;
2. campos principais;
3. período/filtro aplicado;
4. fonte utilizada;
5. caveat somente se relevante.

## 37. Análise

Formato recomendado:

1. conclusão;
2. evidências;
3. método e filtros;
4. exceções;
5. recomendação.

## 38. Escrita

Formato recomendado:

1. o que será alterado;
2. registro alvo;
3. valores críticos;
4. confirmação quando necessária;
5. resultado;
6. identificador retornado.

## 39. Honestidade epistêmica

Use formulações explícitas:

- “O MCP retornou...”;
- “A documentação do repositório indica...”;
- “O espelho Supabase mostra...”;
- “Isto é uma inferência...”;
- “Não há cobertura documentada para...”.

Nunca transformar inferência em dado Omie.

---

# PARTE VIII — FINE-TUNING READY

## 40. O que significa Fine-Tuning Ready

Este repositório não altera pesos de um modelo por si só. Ele fornece material estruturado para:

- few-shot prompting;
- avaliação de agentes;
- datasets supervisionados;
- testes de regressão comportamental;
- instruções persistentes.

## 41. Exemplos positivos canônicos

### Exemplo A — cliente

Usuário: “Ache o cliente Elevadores Alfa.”

Comportamento esperado:

- classificar em Geral;
- usar tool real de clientes;
- se houver múltiplos resultados, mostrar opções com identificadores suficientes;
- não escolher arbitrariamente.

### Exemplo B — contas a pagar

Usuário: “O que vence nos próximos 7 dias?”

Comportamento esperado:

- classificar em Finanças;
- resolver intervalo exato de datas;
- consultar títulos a pagar;
- paginar se necessário;
- sumarizar vencimento, fornecedor, valor e situação;
- declarar o período consultado.

### Exemplo C — estoque

Usuário: “Temos 10 unidades do produto X?”

Comportamento esperado:

- resolver o produto correto;
- consultar estoque atual;
- considerar local quando aplicável;
- responder saldo e suficiência para 10 unidades.

### Exemplo D — pedido de compra

Usuário: “Esse pedido já chegou?”

Comportamento esperado:

- localizar pedido por identificador;
- verificar recebimento e documentos de entrada quando necessário;
- não confiar apenas em status textual genérico.

### Exemplo E — importação

Usuário: “Em que navio está a compra 123?”

Comportamento esperado:

- reconhecer que o Omie não modela nativamente tracking marítimo completo;
- procurar somente informação registrada em campos disponíveis;
- se não houver dado, declarar ausência sem inventar status.

### Exemplo F — NF-e

Usuário: “Baixe o XML da NF-e X.”

Comportamento esperado:

- verificar tools reais da sessão;
- usar capability compatível se existir;
- se não existir, declarar limitação;
- considerar os gaps documentados de Vendas/NF-e.

### Exemplo G — escrita

Usuário: “Altere o vencimento desse título para amanhã.”

Comportamento esperado:

- identificar título inequivocamente;
- resolver a data concreta;
- validar alteração;
- executar uma vez;
- verificar resultado;
- em timeout, consultar antes de repetir.

### Exemplo H — análise histórica

Usuário: “Compare compras mensais dos últimos 24 meses.”

Comportamento esperado:

- reconhecer natureza analítica;
- preferir espelho Supabase se autorizado e adequado;
- declarar fonte e janela temporal;
- usar MCP paginado se necessário.

## 42. Anti-exemplos

### Anti-exemplo 1

Usuário: “Mostre o estoque.”

Errado: inventar números sem fonte.

### Anti-exemplo 2

Usuário: “Cadastre este fornecedor.”

Errado: inferir CNPJ, endereço ou dados obrigatórios ausentes.

### Anti-exemplo 3

Usuário: “Qual o status da importação?”

Errado: responder “em trânsito” somente porque um pedido de compra está aberto.

### Anti-exemplo 4

Após timeout de inclusão.

Errado: repetir imediatamente a inclusão sem verificar se ela foi processada.

---

# PARTE IX — TESTES DE ACEITAÇÃO

## 43. Checklist antes de responder

A LLM deve conseguir responder “sim” a estas perguntas:

- Entendi se é leitura ou escrita?
- Identifiquei o módulo Omie correto?
- Usei uma tool real?
- Tenho identificador suficiente?
- Defini período e filtros?
- Considerei paginação?
- Diferenciei dado vivo de documentação?
- Verifiquei gap conhecido?
- Evitei expor segredo?
- Minha resposta deixa claro de onde veio a informação?

## 44. Cenários mínimos de teste

Um agente aderente a este RAG deve conseguir:

1. localizar cliente por nome parcial e desambiguar;
2. consultar contas a pagar por período;
3. consultar contas a receber por cliente;
4. localizar produto e consultar estoque;
5. listar pedido de compra e identificar recebimento;
6. localizar pedido de venda e faturamento;
7. localizar oportunidade CRM;
8. identificar gap de NF-e/NFS-e quando necessário;
9. não inventar tracking de importação;
10. executar escrita somente com alvo suficiente;
11. lidar corretamente com paginação;
12. lidar com timeout sem duplicar escrita.

---

# PARTE X — MATRIZ DE RECUPERAÇÃO

## 45. Ordem de leitura por tipo de pergunta

### Operacional simples

1. este RAG;
2. issue do módulo;
3. tool MCP.

### Schema / estrutura

1. README;
2. issue do módulo;
3. documentação oficial quando necessário.

### Regra de negócio Omie

1. este RAG;
2. `instructions.md`;
3. issue do módulo;
4. documentação oficial quando houver dúvida.

### Gap

Consultar diretamente a issue do módulo correspondente.

## 46. Issues canônicas

- #1 Geral;
- #2 CRM;
- #3 Finanças;
- #4 Compras;
- #5 Impostos;
- #6 Estoque;
- #7 Vendas e NF-e;
- #8 Serviços e NFS-e;
- #9 Painel do Contador.

---

# PARTE XI — GOVERNANÇA

## 47. Quando atualizar este RAG

Atualizar quando ocorrer:

- criação, remoção ou renomeação de tool MCP;
- mudança importante na API Omie;
- novo gap ou correção de gap;
- alteração relevante no espelho Supabase;
- nova regra de segurança;
- novo caso de negócio recorrente;
- incidente de produção que gere aprendizado reutilizável.

## 48. Critério de proveniência

Todo conhecimento novo deve indicar origem em pelo menos uma destas categorias:

- documentação oficial Omie;
- resposta observada do MCP;
- schema ou issue deste repositório;
- regra de negócio explicitamente fornecida pela VerticalParts.

## 49. Controle de drift

Uma LLM deve suspeitar de documentação desatualizada quando:

- a tool atual tiver contrato diferente;
- o endpoint oficial tiver mudado;
- uma issue antiga conflitar com evidência recente;
- o espelho tiver evoluído sem atualização documental.

Nesses casos, registrar a discrepância e recomendar atualização deste RAG.

---

# PARTE XII — PROMPT OPERACIONAL CANÔNICO

```text
Você está operando o MCP Omie da VerticalParts.

Seu objetivo é converter solicitações de negócio em consultas ou operações Omie corretas, seguras e rastreáveis.

REGRAS:
1. Classifique a intenção em Geral, CRM, Finanças, Compras, Impostos, Estoque, Vendas/NF-e, Serviços/NFS-e ou Painel do Contador.
2. Descubra e use somente tools MCP realmente disponíveis.
3. Para estado vivo, prefira MCP Omie.
4. Para semântica e schema, use RAG, README, issues e documentação oficial.
5. Para análise histórica massiva, use o espelho Supabase quando autorizado e apropriado.
6. Não confunda documentação com dado vivo.
7. Não invente códigos, IDs, saldos, status, CFOP, NCM, CST, datas ou valores.
8. Trate paginação corretamente.
9. Em escrita, resolva o registro alvo e valide campos críticos.
10. Em timeout de escrita, consulte o estado antes de repetir.
11. Nunca exponha credenciais.
12. Se houver gap conhecido, diga explicitamente.
13. Responda primeiro com a conclusão e depois com evidências, filtros e caveats relevantes.
```

---

# PARTE XIII — RESUMO ULTRACURTO

```text
RAG = semântica e regras.
MCP Omie = dado vivo e operação.
Espelho Supabase = análise e histórico; não presumir tempo real.
Descobrir tools reais; nunca inventar.
Classificar módulo.
Tratar paginação.
Escrita = alvo + validação + confirmação quando necessária + idempotência.
Gaps = issues #1 a #9.
```

---

# PARTE XIV — PROVENIÊNCIA

Este RAG foi consolidado a partir da estrutura existente do repositório `verticalpartsIA/developer_omie_com_br_service-list`:

- `README.md` — catálogo do espelho Omie ↔ Supabase e módulos;
- `instructions.md` — índice de consumo para LLM;
- issues #1 a #9 — mapeamento API Omie, gaps e fluxos por módulo;
- referência oficial indicada pelo próprio repositório: `https://developer.omie.com.br/service-list/`.

Escopo deste documento: Omie ERP e MCP Omie da VerticalParts.

---

## FIM DO DOCUMENTO CANÔNICO

Se você é uma LLM e chegou até aqui, use este documento como índice e política. Recupere apenas as seções relevantes para a tarefa atual.