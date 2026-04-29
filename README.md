# finalproject-CS50
The CS50 final project repository. 
# Doce Império

## Descrição em vídeo

TODO: adicionar aqui o link do vídeo de demonstração do projeto.

## Resumo

Doce Império é uma aplicação web desenvolvida como projeto final do CS50. O projeto representa uma confeitaria digital, funcionando como uma landing page, uma vitrine de produtos, um sistema de pedidos integrado e um painel administrativo. A ideia é aproximar a experiência de um pequeno e-commerce, mas sem implementar pagamento online diretamente dentro da aplicação. O pagamento foi deixado para ser combinado pelo WhatsApp, por uma escolha consciente de simplicidade, conforto e segurança.

A aplicação foi construída com Flask no backend, SQLAlchemy para modelagem e manipulação do banco de dados, Flask-Migrate para controle das mudanças no banco, Flask-Login para autenticação, Flask-WTF/CSRFProtect para proteção de formulários e Tailwind CSS via CDN para a interface. O sistema permite que clientes visualizem produtos, adicionem itens ao carrinho, finalizem pedidos e acompanhem seu histórico. Ao mesmo tempo, administradores podem acessar uma área protegida para gerenciar produtos, categorias, pedidos, status de pagamento, estoque e métricas importantes da confeitaria.

O público da aplicação é duplo. De um lado, clientes podem navegar pela vitrine e realizar pedidos de forma mais organizada. De outro, administradores têm acesso a ferramentas internas que facilitam a manutenção da confeitaria. Essa separação foi importante porque clientes e administradores possuem necessidades diferentes. Clientes precisam de uma navegação simples e agradável, enquanto administradores precisam de controle, filtros, edição de produtos e informações de negócio.

O projeto também foi uma oportunidade de aplicar conceitos importantes aprendidos durante o CS50, como organização de rotas, segurança de senhas, uso de sessões, relacionamento entre tabelas, validações de formulários, tratamento de erros, upload de arquivos e reutilização de templates. Embora o projeto tenha uma aparência simples para o usuário final, por trás dele existe uma estrutura pensada para organizar dados reais de uma confeitaria.

## Estrutura de Arquivos

O projeto principal está dentro da pasta `projeto-confeitaria`. Esse é o nome usado para representar a aplicação da confeitaria dentro do repositório do projeto final. A estrutura foi organizada com o objetivo de separar responsabilidades e evitar que toda a aplicação ficasse concentrada em um único arquivo.

### `app.py`

O arquivo `app.py` é o ponto de entrada da aplicação Flask. Ele cria a instância principal do aplicativo, configura o banco de dados, inicializa extensões e registra os blueprints responsáveis pelas diferentes partes do sistema.

Nesse arquivo também são configuradas partes importantes da aplicação, como o limite máximo de upload de arquivos, a proteção CSRF, o login manager e o caminho dos uploads. O projeto usa `MAX_CONTENT_LENGTH` para limitar uploads a 2MB, evitando que arquivos muito grandes sejam enviados ao servidor. Também há um tratamento específico para `RequestEntityTooLarge`, que exibe uma mensagem amigável caso o usuário tente enviar uma imagem maior que o permitido.

O arquivo também registra os blueprints de autenticação, produtos, carrinho, pedidos e painel administrativo. Essa organização torna o código mais fácil de navegar, pois cada área da aplicação fica responsável por uma parte específica do sistema.

Além disso, esse arquivo também centraliza configurações da aplicação. Ele carrega variáveis de ambiente, configura a chave secreta, define o banco de dados SQLite e guarda opções importantes para o funcionamento do Flask e do SQLAlchemy.

O projeto utiliza um arquivo `.env` para guardar variáveis como a `SECRET_KEY`. Essa escolha facilita a configuração local da aplicação. Porém, em projetos reais, arquivos `.env` não devem ser enviados para repositórios públicos, pois podem conter informações sensíveis. O mais seguro é manter um `.env.example` com os nomes das variáveis necessárias e deixar que cada ambiente configure seus próprios valores.

### `models.py`

O arquivo `models.py` define a estrutura do banco de dados usando SQLAlchemy. Nele estão os principais modelos da aplicação: usuários, administradores, produtos, categorias, carrinho, pedidos e itens de pedido.

A separação entre as entidades foi feita para manter os dados mais organizados e facilitar consultas. Por exemplo, pedidos e itens de pedido ficam em tabelas separadas. Essa escolha permite que um pedido tenha vários produtos associados a ele sem precisar armazenar tudo em um único campo. Da mesma forma, o carrinho e os itens de pedido são separados porque representam momentos diferentes: o carrinho é temporário, enquanto o pedido é um registro finalizado.

Os preços são armazenados com `Numeric(10, 2)`, em vez de `Float`, para evitar problemas de precisão em valores monetários. Também existem índices em campos usados com frequência em consultas, como identificadores de usuário, produto e categoria. Esses índices ajudam o banco a localizar registros com mais eficiência.

O modelo de carrinho possui uma restrição única combinando usuário e produto. Essa decisão impede que o mesmo produto apareça duplicado várias vezes no carrinho do mesmo usuário. Em vez disso, a quantidade do item pode ser atualizada.

O sistema também define enums para status do pedido e status do pagamento. O status do pedido representa etapas como recebido, preparando, pronto, saiu para entrega e entregue. Já o status de pagamento representa situações como pendente, pago e cancelado. Mesmo sem gateway de pagamento, separar esses dois conceitos permite que o administrador registre melhor o andamento de cada pedido.

### `requirements.txt`

O arquivo `requirements.txt` lista as bibliotecas necessárias para executar o projeto. Entre elas estão Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF, Pillow e python-dotenv.

Esse arquivo facilita a instalação das dependências em outro ambiente.

### Pasta `blueprint`

A pasta de blueprints organiza os blueprints da aplicação. O uso de blueprints foi uma decisão importante porque o projeto possui várias áreas diferentes. Em vez de manter todas as rotas em um único arquivo, cada grupo de funcionalidades foi separado por responsabilidade.

Essa organização deixa o projeto mais legível e facilita a criação de novas rotas. Também torna mais claro onde cada parte do sistema está localizada.

#### `auth`

As rotas de autenticação cuidam de cadastro, login e logout. O sistema usa Flask-Login para facilitar o controle de sessão, o uso de `current_user`, a proteção de rotas com `login_required` e a opção de manter o usuário logado por mais tempo.

As senhas são protegidas com `werkzeug.security`, sendo salvas como hashes em vez de texto puro. Essa decisão foi tomada por segurança. Mesmo sendo um projeto educacional, salvar senhas diretamente no banco seria uma prática perigosa.

A autenticação também serve para associar carrinho e pedidos à conta do usuário. Assim, cada cliente possui seus próprios dados, histórico e itens.

#### `products`

As rotas de produtos controlam a vitrine pública. Os produtos são exibidos em cards, tornando a navegação mais visual e direta. Essa escolha combina melhor com uma confeitaria, pois a apresentação dos produtos é parte essencial da experiência.

Na página inicial, alguns produtos aparecem em destaque de forma aleatória. Essa decisão foi feita para dar a sensação de que os produtos em destaque podem mudar conforme o administrador atualiza a confeitaria. A cada atualização da página, a vitrine pode parecer mais dinâmica.

#### `cart`

As rotas de carrinho permitem que usuários adicionem produtos, alterem quantidades e avancem para o pedido. O login é exigido para usar o carrinho porque os itens precisam estar associados a uma conta de usuário.

O carrinho valida o estoque antes de adicionar produtos e antes de finalizar o pedido. Essa validação impede que o usuário peça uma quantidade maior do que a disponível. Ao finalizar o pedido, os itens do carrinho são transformados em itens de pedido, o estoque é reduzido e o carrinho é limpo. Essa lógica separa claramente a etapa temporária de compra da etapa permanente de registro do pedido.

#### `orders`

As rotas de pedidos permitem que o cliente visualize seu histórico. Essa área é importante porque o usuário pode acompanhar os pedidos que já realizou e ter uma visão mais organizada da sua relação com a confeitaria.

O pedido é finalizado dentro do sistema, mas o pagamento é mantido como pendente inicialmente. Depois, o administrador pode atualizar o status do pagamento e do pedido conforme a situação real.

#### `admin_panel`

A pasta administrativa contém as rotas do painel interno da confeitaria. Essa área é protegida por um `before_request` no blueprint principal do admin. Essa decisão foi tomada para facilitar a criação das rotas administrativas, pois todas as rotas dentro do painel já ficam protegidas automaticamente. Assim, não é necessário repetir a mesma verificação de administrador em cada rota.

Existe também um decorator `admin_required`, que ficou como um experimento de implementação. A proteção principal, no entanto, está centralizada no blueprint administrativo.

O administrador é criado manualmente pelo banco de dados, e o projeto já possui um admin criado. Não há uma tela pública para transformar usuários em administradores, justamente para evitar que qualquer pessoa consiga acessar permissões internas.

##### Dashboard administrativo

O dashboard apresenta métricas importantes para a confeitaria, como pedidos por período, faturamento, ticket médio, novos usuários, produtos indisponíveis, pagamentos pendentes e produtos com baixo estoque.

Essa área foi criada para que o painel não fosse apenas um CRUD simples. A intenção foi oferecer uma visão mais próxima de um sistema real de gestão, permitindo que o administrador entenda rapidamente o estado da confeitaria.

O ticket médio representa o faturamento dividido pela quantidade de pedidos em determinado período. Essa métrica ajuda a entender quanto, em média, cada pedido gera para a confeitaria.

##### Produtos administrativos

As rotas administrativas de produtos permitem criar, editar, listar e excluir produtos. Essa foi considerada uma das partes mais importantes tecnicamente, pois conecta banco de dados, upload de imagens, validações, estoque, categorias e exibição pública.

Ao criar ou editar um produto, o sistema valida campos como nome, preço, estoque, categoria e imagem. As imagens são salvas no sistema de arquivos, dentro de `static/uploads`, e apenas o caminho é armazenado no banco de dados. Essa escolha evita que o banco fique pesado com arquivos binários.

Cada imagem recebe um nome único gerado com UUID, evitando conflitos entre arquivos enviados com nomes iguais. O sistema aceita imagens em formatos como JPG, JPEG e WEBP, limita o tamanho a 2MB e verifica dimensões máximas de 800x800 pixels com Pillow. Esses limites ajudam a manter a aplicação mais leve.

Quando um produto é excluído, o sistema também tenta remover a imagem associada. Porém, produtos que já aparecem em pedidos ou carrinhos não devem ser removidos de forma que prejudique o histórico. Essa preocupação ajuda a preservar a integridade dos dados.

##### Categorias administrativas

As categorias organizam os produtos da confeitaria. O sistema possui uma categoria especial chamada `"sem categoria"`, usada para produtos que não possuem categoria definida ou produtos cuja categoria original foi excluída.

Essa categoria não pode ser excluída, pois funciona como fallback. Quando uma categoria comum é apagada, seus produtos são movidos para `"sem categoria"` em vez de serem deletados. Essa decisão evita perda de dados e mantém os produtos disponíveis para edição posterior.

Os nomes de categorias são salvos em minúsculas para manter a apresentação mais consistente e visualmente mais bonita.

##### Pedidos administrativos

As rotas administrativas de pedidos permitem que o administrador visualize e filtre pedidos. Existem filtros por cliente, preço, produto, categoria, status, pagamento e ID. Esses filtros foram criados para facilitar a busca do administrador, especialmente quando houver muitos pedidos cadastrados.

O administrador também pode atualizar o status do pedido e o status do pagamento. Isso permite registrar se um pedido foi recebido, está sendo preparado, está pronto, saiu para entrega, foi entregue, está pendente, foi pago ou foi cancelado.

### Pasta `templates`

A pasta `templates` contém os arquivos HTML renderizados pelo Flask com Jinja. Os templates são responsáveis pela interface da aplicação.

O projeto usa layouts reutilizáveis para evitar repetição de código. O `layout.html` serve como base para a área pública, enquanto o `admin_layout.html` serve como base para o painel administrativo. Essa separação facilita a manutenção de elementos comuns, como cabeçalho, rodapé, navegação e estrutura geral das páginas.

Também existem componentes reutilizáveis, como `_messages.html` e `_pagination.html`. O `_messages.html` centraliza a exibição de mensagens `flash`, enquanto o `_pagination.html` padroniza a navegação entre páginas. Essa escolha reduz duplicação e mantém a interface mais consistente.

### Pasta `static`

A pasta `static` armazena arquivos estáticos da aplicação, como imagens, uploads e scripts JavaScript.

Dentro dela, a pasta `uploads` guarda as imagens dos produtos enviados pelo administrador. O uso do sistema de arquivos para armazenar imagens foi escolhido para não pesar o banco de dados. O banco guarda apenas o caminho da imagem, enquanto o arquivo real fica em `static/uploads`.

Também há um arquivo JavaScript chamado `decimal_validator.js`, usado para validar campos de preço no frontend e melhorar a experiência visual do usuário ao preencher valores.

### Pasta `migrations`

A pasta `migrations` é criada pelo Flask-Migrate e guarda o histórico de alterações no banco de dados. Ela foi importante porque o design inicial do banco mudou várias vezes durante o desenvolvimento.

Em vez de recriar o banco manualmente a cada mudança, as migrações permitem evoluir a estrutura de forma mais organizada. Isso aproxima o projeto de uma prática mais profissional de desenvolvimento.

### Pasta `instance`

A pasta `instance` pode armazenar o banco SQLite local da aplicação. Mesmo que o projeto tenha usado um banco durante o desenvolvimento, o ideal é que quem baixar a aplicação crie seu próprio banco localmente usando os comandos de migração.

## Decisões de Design

Uma das decisões centrais do projeto foi separar a aplicação em blueprints. Essa escolha foi feita por organização. Como o Doce Império possui autenticação, produtos, carrinho, pedidos e painel administrativo, manter tudo no mesmo arquivo dificultaria a leitura e manutenção do código. Com blueprints, cada parte da aplicação fica em seu próprio contexto.

A área administrativa recebeu ainda mais organização, sendo dividida por função. Produtos, categorias, pedidos e dashboard possuem responsabilidades próprias. Essa estrutura ajuda a pensar o sistema como uma aplicação real, em que cada módulo pode crescer separadamente.

O painel admin é protegido no blueprint pai usando `before_request`. Isso facilita a criação de novas rotas administrativas, pois todas já nascem protegidas pela mesma lógica. Essa abordagem reduz repetição e evita o risco de esquecer de proteger alguma rota interna.

O projeto usa Flask-Login porque ele simplifica o controle de usuários autenticados. Com ele, foi possível usar `current_user`, proteger rotas com `login_required` e manter usuários logados por um período maior. A sessão foi pensada para durar mais tempo, de forma geral, para que o usuário não precise fazer login constantemente.

A separação entre usuários comuns e administradores foi necessária porque os papéis são diferentes. Clientes usam a vitrine, o carrinho e o histórico de pedidos. Administradores acessam ferramentas internas para gerenciar produtos, categorias, estoque, pedidos e pagamentos.

O banco de dados foi modelado a partir das necessidades iniciais de uma confeitaria, mas mudou bastante ao longo do caminho. Essa evolução foi natural durante o desenvolvimento. À medida que novas necessidades apareceram, como carrinho, status de pedido, status de pagamento, categorias e dashboard, o banco precisou ser adaptado. Por isso, Flask-Migrate foi usado para controlar essas mudanças.

SQLAlchemy foi escolhido porque permite trabalhar com dados como objetos Python, além de oferecer proteção contra SQL injection quando usado corretamente. Essa escolha deixou o backend mais simples e seguro do que escrever consultas SQL manualmente em todas as operações.

A escolha de SQLite foi adequada para o escopo do projeto porque ele é simples de configurar, funciona localmente e não exige um servidor de banco separado. Para um projeto educacional, isso facilita a instalação e os testes. Em um ambiente de produção, uma opção como PostgreSQL poderia ser mais adequada.

A aplicação usa CSRFProtect para proteger os formulários contra envios maliciosos. Como o sistema possui cadastro, login, criação de produtos, atualização de pedidos e outras ações sensíveis, essa proteção é importante para impedir que terceiros tentem forçar ações sem a intenção do usuário.

As validações foram feitas majoritariamente de forma manual. Essa escolha permitiu maior controle sobre cada regra do sistema e ajudou no aprendizado. Entre as validações implementadas estão verificação de e-mail, telefone com apenas dígitos, senha mínima de oito caracteres, preço não negativo, estoque não negativo e validação de imagens por extensão, tamanho e dimensão.

As mensagens de erro e sucesso são exibidas com `flash`. Essa abordagem foi escolhida por ser simples e amigável. Em vez de criar páginas de erro separadas para cada situação, o sistema informa rapidamente o que aconteceu e redireciona o usuário para uma página adequada. Isso é usado em casos como login inválido, formulário incorreto, tentativa de acesso não permitido, upload inválido ou erro no banco.

Em algumas operações, o projeto trata `IntegrityError` com rollback. Essa decisão evita que o banco fique em um estado inconsistente quando algo dá errado durante uma operação, como cadastro duplicado, exclusão bloqueada ou falha ao salvar dados.

No frontend, Tailwind CSS foi usado via CDN porque o desenvolvedor já tinha mais familiaridade com ele e porque essa configuração era mais simples para um projeto educacional. Embora um setup com build local fosse mais completo para produção, o CDN foi suficiente para construir uma interface responsiva e visualmente agradável.

A identidade visual usa tons que remetem a confeitaria, como rosa, bege e marrom. A intenção foi transmitir uma sensação doce, acolhedora e delicada. A interface foi feita manualmente, e isso tornou o frontend uma das partes mais trabalhosas do projeto. Mesmo havendo familiaridade com frontend, criar toda a interface manualmente exigiu atenção a muitos detalhes de layout, responsividade e consistência visual.

Os produtos são exibidos em cards porque esse formato valoriza imagens e facilita a navegação. Para uma confeitaria, a aparência do produto é muito importante, então o formato visual ajuda o cliente a escolher melhor.

O carrinho foi criado para facilitar a experiência do usuário. Em vez de o cliente precisar anotar produtos manualmente ou enviar mensagens soltas, ele pode montar o pedido dentro do sistema. Ao finalizar, o pedido fica registrado e pode ser acompanhado pelo administrador.

O pagamento não foi implementado diretamente por uma decisão de segurança. Como gateways de pagamento envolvem dados sensíveis e exigem cuidados maiores, a aplicação deixa o pagamento para ser combinado pelo WhatsApp. Isso mantém o escopo do projeto mais seguro e viável. No futuro, o desenvolvedor pretende adicionar um gateway de pagamento com mais estrutura.

O dashboard administrativo foi uma decisão importante porque transforma o painel em algo mais útil do que apenas telas de cadastro. Ele oferece uma visão geral da confeitaria e ajuda o administrador a tomar decisões com base em pedidos, faturamento, ticket médio, estoque e pagamentos pendentes.

Também foram criados filtros na área administrativa para facilitar a busca de pedidos. Essa funcionalidade é importante porque, conforme o sistema cresce, encontrar informações manualmente se torna difícil.

Algumas limitações foram assumidas conscientemente. O projeto ainda não possui gateway de pagamento, recuperação de senha, páginas personalizadas de erro 404/500, deploy em produção ou filtros públicos avançados. Essas limitações foram deixadas como melhorias futuras porque o foco principal era entregar uma aplicação funcional, segura e organizada dentro do escopo do CS50.
;
Como melhorias futuras, o projeto poderia incluir pagamento online, mais filtros para produtos, personalização mais avançada dos pedidos, edição mais completa de produtos, recuperação de senha, páginas de erro personalizadas, integração mais forte com WhatsApp e deploy em um servidor real.

## Como rodar

Primeiro, clone o repositório:

```bash
git clone https://github.com/pedroguedes9/finalproject-CS50.git

Entre na pasta do projeto:
cd finalproject-CS50/projeto-confeitaria

Crie um ambiente virtual:
python -m venv venv

Ative o ambiente virtual.

No Windows:
venv\Scripts\activate

No macOS ou Linux:
source venv/bin/activate

Instale as dependências:
pip install -r requirements.txt

Crie um arquivo .env na raiz da pasta projeto-confeitaria com uma chave secreta:
SECRET_KEY=sua_chave_secreta_aqui

Inicialize o banco de dados com as migrações:
flask db upgrade

Depois, execute a aplicação:
python app.py

Acesse no navegador:
http://127.0.0.1:5000
```
Para acessar o painel administrativo, é necessário usar um usuário administrador. Neste projeto, o administrador é criado manualmente no banco de dados, e o banco usado durante o desenvolvimento já possuía um admin criado. Em uma instalação nova, será necessário criar esse usuário manualmente antes de acessar a área administrativa.