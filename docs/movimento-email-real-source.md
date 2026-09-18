# Movimento Email — origem SQL corporativa no PC24x7

## Objetivo
Executar continuamente, em DEV, a leitura somente leitura da origem SQL corporativa da Prospecção Movimento e promover os dados para a camada canônica `movimento_src` do banco persistente DEV.

## Segurança
- O repositório contém somente referências; nenhum DSN é versionado.
- A origem exige ODBC Driver 18 com criptografia e certificado validado.
- Os DSNs ficam em arquivos protegidos no host e são montados como Docker secrets.
- O processo rejeita alvo cujo nome do banco não termine em `Dev`.
- A origem recebe somente comandos `SELECT`.

## Arquivos protegidos esperados
- `MOVIMENTO_EMAIL_SOURCE_DSN_FILE`: DSN real da origem corporativa.
- `MOVIMENTO_EMAIL_TARGET_DSN_FILE`: DSN do SQL DEV persistente.
- `MOVIMENTO_EMAIL_SOURCE_MAP_FILE`: mapeamento dos quatro objetos reais descobertos pelo RDL/RDS ou pelo DBA.

Permissões recomendadas: somente a conta que executa o Docker deve conseguir ler os dois arquivos de DSN.

## Subida
1. Atualizar o checkout ReqSys para o SHA aprovado.
2. Copiar `movimento-email-real-source.env.example` para um arquivo local fora do Git.
3. Preencher apenas caminhos e SHA, nunca valores de DSN.
4. Criar o mapeamento real a partir do exemplo versionado no ReqSys.
5. Executar:
   `docker compose --env-file <arquivo-local> -f docker-compose.movimento-email-real-source.yml up -d --build`.

## Evidência
Cada ciclo executa:
1. dry-run sem escrita;
2. apply no alvo DEV;
3. repetição idêntica, que deve retornar `already_present_no_write`.

A evidência fica em `MOVIMENTO_EMAIL_EVIDENCE_DIR` e não contém linhas de negócio, CPF, usuário, senha ou connection string.

## Critério de conclusão
- container saudável;
- `synthetic=false`;
- `corporate_source_validated=true`;
- `business_data_observed=true` para pelo menos uma execução;
- contagens das views V2 compatíveis;
- repetição sem escrita;
- nenhuma alteração em HML/PROD.
