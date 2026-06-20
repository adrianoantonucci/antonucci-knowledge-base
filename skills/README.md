# Convenção de Skills

Esta pasta segue o formato oficial de **Agent Skills** usado por Claude Code, Cowork e claude.ai.

## Estrutura obrigatória

Cada skill é uma **pasta própria** contendo um arquivo `SKILL.md`:

```text
skills/
├── nome-da-skill/
│   └── SKILL.md
└── outra-skill/
    ├── SKILL.md
    └── references/      (opcional — docs carregados sob demanda)
```

Nunca criar `.md` solto direto em `skills/` ou em subpastas temáticas (`content/`, `leadership/`). Isso não é descoberto pelo sistema de Skills.

## Frontmatter obrigatório

Todo `SKILL.md` começa com:

```yaml
---
name: nome-da-skill
description: O que a skill faz E quando usá-la, com gatilhos explícitos (frases que o usuário diria). Seja "pushy" aqui — é o único campo sempre carregado em contexto, e é ele que decide se a skill é ativada.
---
```

A `description` é o mecanismo de ativação. Se ela for vaga, a skill nunca dispara. Inclua sinônimos e frases reais que Adriano usaria.

## Como decidir: Skill vs. CLAUDE.md vs. memory/

| Tipo de conteúdo | Onde colocar |
| --- | --- |
| Comportamento/framework que só importa em tarefas específicas (ex: revisar arquitetura, escrever post) | `skills/` |
| Identidade, preferências, objetivos, stack — sempre relevante, curto | `CLAUDE.md` |
| Fatos sobre o ambiente, perfil, histórico — referência, não comportamento | `memory/`, `knowledge/` |

Evite duplicar o mesmo framework no `CLAUDE.md` e em uma skill. O `CLAUDE.md` é carregado em **toda** conversa — deve ficar leve. As skills carregam só quando o gatilho bate (progressive disclosure).

## Skills atuais

- **linkedin-writer** — geração de conteúdo de LinkedIn a partir de experiências reais.
- **staff-engineer-advisor** — análise estratégica de decisões técnicas/arquiteturais/organizacionais.

## Adicionando uma nova skill

1. `mkdir skills/nome-da-skill`
2. Criar `skills/nome-da-skill/SKILL.md` com frontmatter `name` + `description`.
3. Rodar `python3 scripts/sync_marketplace.py` para validar e atualizar `.claude-plugin/marketplace.json` automaticamente.
4. Se a skill precisar de scripts ou docs de referência grandes, colocar em `skills/nome-da-skill/scripts/` ou `references/` — não inflar o `SKILL.md` principal (manter abaixo de ~500 linhas).

## Instalação e atualização por superfície

`claude.ai`, Claude Code e Cowork **não compartilham skills entre si** — cada um tem seu próprio mecanismo. Resumo:

| Superfície | Como instalar (1x) | Como atualizar depois |
| --- | --- | --- |
| **Claude Code** | `claude plugin marketplace add adrianoantonucci/antonucci-knowledge-base` depois `/plugin install antonucci-skills@antonucci-knowledge-base` | `/plugin marketplace update` |
| **Cowork (pessoal)** | Customize > Plugins > Add plugin (GitHub) > `adrianoantonucci/antonucci-knowledge-base` | Botão "Sync" no mesmo painel |
| **Cowork (organização)** | Organization settings > Plugins > Add plugin (GitHub) | Automático — Cowork sincroniza do repo periodicamente |
| **claude.ai (web/mobile)** | Settings > Capabilities > Skills > Upload do `.zip` | Manual: baixar o `.zip` mais recente da [última release](../../releases) e subir de novo |

### Por que claude.ai é manual

Custom Skills no claude.ai não sincronizam com GitHub — é uma limitação da plataforma, não deste repositório. O workflow `.github/workflows/docs.yaml` já gera um `.zip` por skill a cada push que altera `skills/` e publica como GitHub Release, então a parte de "gerar o pacote certo" é automática; só falta o clique de upload.

### Automação no CI

A cada push em `main`:

1. `scripts/sync_marketplace.py --check` valida o frontmatter de todo `SKILL.md` (falha o build se algo estiver quebrado).
2. Se algo em `skills/` mudou, `scripts/package_skills.py` gera os `.zip` e o workflow publica uma nova Release com eles.
