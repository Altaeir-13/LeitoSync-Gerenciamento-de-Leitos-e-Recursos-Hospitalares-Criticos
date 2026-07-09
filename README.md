# LeitoSync — Gerenciamento de Leitos e Recursos Hospitalares Críticos

Um sistema distribuído para gerenciamento de leitos e recursos hospitalares críticos, focado em resolver problemas de concorrência e consistência de dados.

## Relação com o problema dos leitores e escritores

O LeitoSync aplica a lógica do problema clássico dos leitores e escritores em um cenário distribuído de gestão de leitos e recursos hospitalares. As operações de consulta de disponibilidade representam os leitores, pois múltiplos usuários podem acessar simultaneamente o estado dos recursos sem modificá-lo. Já operações como reserva, ocupação, liberação, bloqueio ou manutenção representam os escritores, pois alteram o estado compartilhado de um recurso crítico. Para evitar inconsistências, como a reserva duplicada de um mesmo leito, o sistema utiliza transações no PostgreSQL com bloqueio pessimista por linha. Os testes automatizados demonstram que múltiplas leituras simultâneas são atendidas com sucesso, enquanto múltiplas tentativas concorrentes de escrita sobre o mesmo recurso resultam em apenas uma reserva confirmada, rejeitando as demais com erro de conflito.

Observação: o sistema usa PostgreSQL com transações e bloqueio pessimista por linha para evitar reserva duplicada.

## Tecnologias utilizadas

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pytest.
- **Frontend**: Node 22, React, TypeScript, Vite, Tailwind CSS.
- **Infraestrutura**: Docker, Docker Compose.

## Estrutura de pastas

```
leitossync/
  backend/
    app/
    alembic/
    tests/
    Dockerfile
    requirements.txt
    pytest.ini
    entrypoint.sh
  frontend/
    src/
    public/
    Dockerfile
    package.json
    package-lock.json
    vite.config.ts
    tailwind.config.js
    postcss.config.js
    index.html
  docker-compose.yml
  README.md
  .gitignore
```

## Como executar com Docker Compose

Para subir o ambiente completo (banco de dados, backend e frontend), execute:

```bash
docker compose up --build
```

### Acessos

```text
Frontend: http://localhost:5173
Backend: http://localhost:8000
Swagger: http://localhost:8000/docs
```

## Como rodar os testes

Com os containers em execução, você pode rodar a suíte de testes no backend usando:

```bash
docker compose exec backend pytest -v
```

Evidência esperada dos testes: `8 passed`.

## Testes de concorrência

A suíte de testes automatizados valida casos clássicos de concorrência para garantir a consistência do sistema. A suíte valida:

* múltiplas leituras simultâneas;
* reserva de recurso disponível;
* rejeição de reserva duplicada;
* múltiplos escritores concorrentes;
* leitores durante tentativa de escrita;
* criação de apenas uma reserva ativa;
* criação de log de auditoria após escrita.

## Leitores e Escritores no contexto do sistema

- **Leitores**: Operações de listagem, consulta e visualização de leitos e recursos. Diversos usuários (leitores) podem verificar o painel simultaneamente.
- **Escritores**: Operações de reserva, ocupação, liberação ou manutenção. Exigem acesso exclusivo àquele registro para não haver conflito de estado, implementado via transação com bloqueio no banco de dados.
