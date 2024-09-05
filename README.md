# Sistema de Notas e Frequência - Teste Prático DTI Digital

Este projeto é minha versão do teste prático para estágio em desenvolvimento na DTI Digital.

## Acesso ao Sistema

Acesse o sistema através do link: [https://5cf8-2804-540-d018-9c00-f5fb-9dfe-b616-9dbc.ngrok-free.app/](https://5cf8-2804-540-d018-9c00-f5fb-9dfe-b616-9dbc.ngrok-free.app/)

**OBS:** O sistema está hospedado remotamente devido ao curto tempo para aprender e minha falta de experiência prévia em deploy. Não foi possível subir o sistema para plataformas como Heroku ou Vercel.

## O Problema

Carlos é um professor que precisa organizar as notas e a frequência de seus alunos. Cada aluno tem uma nota para cada uma das cinco disciplinas que Carlos ensina e um registro de presença para cada aula. O sistema permite que Carlos insira as notas de cada aluno (0 a 10) nas cinco disciplinas e a frequência de cada aluno em percentual (0 a 100%). 

### Funcionalidades
- Cálculo automático da média das notas de cada aluno
- Cálculo da média da turma em cada disciplina
- Cálculo da frequência geral de cada aluno
- Visualização de alunos com média acima da média da turma
- Visualização de alunos com frequência abaixo de 75%

## Premissas Assumidas

- Uso exclusivo por Carlos, sem necessidade de autenticação multi-usuário
- Cinco disciplinas fixas e pré-definidas
- Uma nota única por disciplina por aluno
- Notas na escala de 0 a 10, permitindo decimais
- Frequência calculada considerando todas as aulas de todas as disciplinas
- Média do aluno como média simples das cinco disciplinas
- Média da turma como média simples das notas de todos os alunos por disciplina
- Sem armazenamento de datas específicas de aulas ou faltas
- Sem requisitos específicos para edição ou exclusão de dados após inserção

## Decisões de Projeto

O projeto explora tecnologias essenciais na criação de sistemas:

- Ambiente de design para layout do front-end
- Código de back-end com a lógica do sistema
- Código de front-end para estilização e apresentação (UI design)
- Banco de dados para armazenamento com sistema CRUD
- API para conexão entre back-end, front-end e banco de dados

## Tecnologias Utilizadas

- **Ambiente de Design:** Figma
- **Back-end:** Python
- **Banco de Dados:** PostgreSQL
- **API:** Flask
- **Front-end:** React com Bootstrap para estilização

## Características Adicionais

- Hospedagem remota

---

Para mais informações ou dúvidas sobre o projeto, entre em contato.
