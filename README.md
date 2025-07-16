# 🛰️ PYTHON BROADCAST

**PYTHON BROADCAST** é uma plataforma para **compartilhamento seguro de aplicações Python**, funcionando como uma loja de aplicativos local. Ele gerencia, instala, isola e protege seus projetos, garantindo segurança e praticidade para desenvolvedores e usuários.

---

## 🚀 Funcionalidades

- Compartilhamento de projetos Python com facilidade.
- Armazenamento seguro com **dupla criptografia (AES + RSA 512 bits)**.
- Instalação automatizada em ambiente isolado.
- Interface amigável para publicação e execução dos apps.
- Código-fonte protegido contra exposição.

---

## 📁 Estrutura do Projeto

Cada aplicação Python deve conter obrigatoriamente na **raiz do projeto**:

### 1. `config.json`

Define os metadados do app. Exemplo:

```json
{
  "app_name": "Agent Studio",
  "app_file": "agent studio.py",
  "app_icon": "icons\\logo.png",
  "args": "",
  "author": "tarcisio.b.prates",
  "version": "1.0.0"
}
```

### 2. `requirements.txt`

Arquivo padrão contendo todas as dependências do projeto, para que o ambiente virtual seja corretamente configurado.

---

## 🔒 Segurança

- O projeto é **comprimido** em um arquivo `.zip` criptografado com **AES**.
- Em seguida, esse arquivo é **criptografado com uma chave RSA de 512 bits**.
- A descriptografia dos arquivos ocorre **somente no momento da execução**, evitando exposição do código-fonte.

---

## 🛠️ Instalação e Execução

1. O app instalado será extraído para o diretório `C:\\_apps\\<nome_do_app>`.
2. Dentro da pasta, será criado um **ambiente virtual (.venv)**.
3. As dependências definidas no `requirements.txt` serão automaticamente instaladas.
4. A execução será feita com segurança, com os arquivos descriptografados apenas temporariamente.

---

## 👤 Autor

**Tarcisio B. Prates**  
Desenvolvedor do PYTHON BROADCAST  
📧 tarcisio.b.prates

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.