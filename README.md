# ReqSys Infrastructure — PC24x7

Infraestrutura auxiliar e contratos operacionais do host PC24x7 do ReqSys.

> **Fonte canônica do runtime DEV:** a orquestração ativa do ReqSys DEV pertence ao repositório
> `ericson-j-santos/reqsys-v2-enterprise-real`. Este repositório não mantém uma segunda
> implementação concorrente de deploy/runtime.

## Estado atual

| Responsabilidade | Fonte canônica |
|---|---|
| Runtime ReqSys DEV | `reqsys-v2-enterprise-real` |
| Supervisor local DEV | Windows Scheduled Task `ReqSys-Dev-Runtime-Supervisor` |
| Exposição pública DEV | Cloudflare Quick Tunnel + locator assinado |
| Validação de saúde | `/api/health`, `/api/runtime/health`, `/api/runtime/build-info` |
| Evidência de publicação | deve usar o `expected_sha` imutável da execução |
| Infraestrutura auxiliar / contratos do host | este repositório |
| HML / PROD | fora deste incremento; nenhuma automação de deploy é declarada aqui |

O contrato versionado está em `config/pc24x7-dev-ownership.json`. O workflow
`PC24x7 Repository Contract` valida esse contrato sem executar deploy, alterar
segredos, promover ambiente ou tocar HML/PROD.

## Ownership do DEV

O runtime atual é implementado no repositório principal por estes componentes canônicos:

- `scripts/pc24x7_dev_runtime_supervisor.py`
- `scripts/pc24x7_dev_runtime_supervisor_install.py`
- `scripts/pc24x7_dev_locator_publisher.py`
- `scripts/resolve_pc24x7_dev_locator.mjs`
- `scripts/validate_publication_sync.py`
- `infra/public-access-urls.json`
- `.github/workflows/fly-automatic-environment-promotion.yml`

O nome do último workflow é legado; o contrato atual suporta o provedor `pc24x7`.
A infraestrutura não deve copiar essa lógica. Mudanças de runtime devem ocorrer na
fonte canônica e chegar aqui apenas como contrato/integração de host.

## Arquivos locais garantidos pelo contrato

O bloco abaixo é validado automaticamente. Se um caminho deixar de existir, ou a
documentação divergir do manifesto, o CI falha fechado.

<!-- PC24X7_CONTRACT_PATHS_START -->
- `README.md`
- `config/pc24x7-dev-ownership.json`
- `scripts/validate_repository_contract.py`
- `.github/workflows/repository-contract-ci.yml`
- `systemd/reqsys-dev.service`
- `systemd/reqsys-hml.service`
- `systemd/reqsys-prod.service`
- `systemd/reqsys.service.template`
- `systemd/README.md`
- `docker-compose.movimento-email-real-source.yml`
- `movimento-email-real-source.env.example`
- `docs/movimento-email-real-source.md`
- `.github/workflows/movimento-email-real-source-ci.yml`
<!-- PC24X7_CONTRACT_PATHS_END -->

## Systemd

Os arquivos em `systemd/` permanecem como templates de infraestrutura Linux/WSL2 e
referência histórica. **Eles não representam o mecanismo ativo do Desktop PC24x7 DEV**,
que atualmente usa Windows Scheduled Task.

Não assumir que existam scripts de instalação, health check, backup ou workflows de
deploy apenas porque foram descritos em versões anteriores deste README. Somente os
caminhos do bloco contratual acima são garantidos localmente.

## Movimento Email — fonte real

A frente de Movimento Email possui infraestrutura própria neste repositório:

- `docker-compose.movimento-email-real-source.yml`
- `movimento-email-real-source.env.example`
- `docs/movimento-email-real-source.md`
- `.github/workflows/movimento-email-real-source-ci.yml`

Credenciais reais não devem ser versionadas. O compose consome arquivos/variáveis
provisionados no host.

## Controles obrigatórios do runtime DEV

O contrato de integração exige:

1. `expected_sha` exato; evidência de outro SHA não libera a execução.
2. Os três endpoints de saúde/runtime antes de considerar a publicação pronta.
3. Locator público assinado e fail-closed.
4. HML e PROD fora do escopo deste CI.
5. O CI deste repositório é somente de contrato; **não executa deploy**.

A validação local do contrato é:

```bash
python -m py_compile scripts/validate_repository_contract.py
python scripts/validate_repository_contract.py
```

Resultado esperado: JSON com `"status": "passed"`,
`"exact_expected_sha_required": true`, `"hml_prod_touched": false` e
`"deploy_executed": false`.

## Política de custo

A estratégia permanece de custo adicional zero:

- PC 24x7 já disponível;
- Cloudflare Quick Tunnel no plano gratuito;
- GitHub Actions hospedado para validações de contrato;
- nenhuma dependência paga é introduzida por este incremento.

## Critério para considerar DEV comprovado

Este repositório, isoladamente, **não comprova que o runtime DEV está publicado**.
A conclusão exige evidência do repositório principal e do runtime no mesmo SHA:
saúde, `build-info`, locator vigente e validação pós-publicação.

Enquanto o runner/host físico não produzir essa evidência, o estado deve permanecer
parcial/bloqueado — nunca “concluído” por documentação ou CI estático.
