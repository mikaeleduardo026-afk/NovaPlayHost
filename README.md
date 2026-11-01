# NovaPlayHost — pacote de sites

## Estrutura

- `lumora/` — plataforma Lumora
- `scriptlab/` — academia ScriptLab SA
- `mta-asset-viewer/` — visualizador e empacotador para MTA:SA
- `token-generator/` — painel local de emissão de tokens (rota administrativa; noindex)
- `index.html` — portal inicial com links para os três produtos públicos
- `legal.html` — políticas gerais da marca

Cada site inclui seu próprio `index.html` e `legal.html`. Os quatro rodapés levam ao Discord oficial e às políticas.

## Atenção antes de publicar

1. Lumora e ScriptLab, nas versões recebidas, utilizam `localStorage` para contas/progresso; não existe backend de autenticação nem banco de dados online nesses arquivos. Publicar o HTML não transforma isso em login compartilhado.
2. O gerador de tokens armazena o cofre cifrado no navegador. Exporte e proteja o backup `.slkey` do cofre já utilizado. Não crie uma chave nova nem substitua a chave pública dos sites sem uma migração coordenada. O pacote adiciona o produto `assetviewer` ao mesmo formato Ed25519 SL2.
3. O Asset Viewer requer token com `app: "assetviewer"`, assinado pela mesma chave pública configurada nos outros sites. A validação local do token não oferece revogação central nem proteção forte contra reutilização entre navegadores; isso exige backend.
4. A geração de resource MTA:SA copia DFF/TXD/COL como bytes originais e gera `meta.xml` e `client.lua`. O DFF é carregado após COL e TXD, conforme a orientação da Wiki MTA. Arquivos incompatíveis não são reparados automaticamente.
5. As páginas legais são rascunhos operacionais, não parecer jurídico. Complete a identificação legal do fornecedor e confirme hospedagem, retenção de logs, formas de pagamento e procedimentos comerciais antes de iniciar vendas.
6. O ZIP é um pacote estático; ele ainda não foi publicado na internet. O portal inicial não divulga o gerador de tokens, cuja rota administrativa permanece acessível se o diretório for publicado; `noindex` não é autenticação nem bloqueio de acesso.


## Navegação entre os sites

Os links internos agora apontam diretamente para os arquivos `index.html` de cada plataforma e permanecem no mesmo domínio. Publique a pasta inteira mantendo a estrutura original. Abra o endereço público de hospedagem (por exemplo, o endereço do Pages/host), não o botão `Go to file`, a visualização do repositório ou os links `tree/main` do GitHub. Na visualização do repositório, o GitHub mostra pastas e arquivos; isso não é a página publicada.

## Publicação

O conteúdo pode ser publicado como um único site estático mantendo as quatro pastas na raiz, para preservar os links relativos. Configure como diretório de publicação a raiz deste pacote. O painel de tokens deve permanecer restrito ao responsável pela operação; a autenticação local atual não equivale a controle de acesso no servidor.
