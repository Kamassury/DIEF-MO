# DIEF-MO  
**AI-Ready Multi-Omics Data Integration & Encoding Framework**

## Overview
A integração de dados multi-ômicos é essencial para a análise de sistemas biológicos complexos e para aplicações em Inteligência Artificial (IA). No entanto, desafios como heterogeneidade, ausência de padronização e falta de rastreabilidade comprometem a qualidade e a reprodutibilidade das análises.

O **DIEF-MO** foi desenvolvido para resolver esses problemas por meio de um framework estruturado de **padronização, codificação e data lineage**, preparando os dados para integração e uso em modelos de machine learning.

---

## Objective
Desenvolver um framework de codificação padronizada para dados multi-ômicos que:
- Preserve a rastreabilidade completa dos dados (*data lineage*)
- Estruture experimentos e amostras de forma consistente
- Permita integração entre diferentes áreas e tipos de dados
- Prepare os dados para aplicação em modelos de IA

---

## Methodology

O framework utiliza um **identificador único padronizado para cada ensaio**, composto por subcódigos que representam:

- Área responsável  
- Tipo de atividade (experimental ou literatura)  
- Matriz analisada  
- Sequência do ensaio  

### Estrutura do identificador (exemplo)

E001_PRO_M001_nnn


Onde:
- `E001` → Código do experimento  
- `PRO` → Área responsável  
- `M001` → Código da matriz/amostra  
- `nnn` → Identificador sequencial  

---

## Core Entities

O modelo é estruturado em cinco entidades principais:

- **area_code** → Área responsável pelo ensaio  
- **activity_code** → Origem do dado (experimental ou literatura)  
- **matrix_code** → Identificação da matriz analisada  
- **matrix_type** → Tipo da matriz  
- **experiment_code** → Identificação do experimento  

Entidades secundárias são derivadas dessas estruturas para representar:
- Amostras  
- Lotes  
- Sequências experimentais  

---

## Key Features

- ✅ Padronização de dados multi-ômicos  
- ✅ Rastreabilidade completa (*data lineage*)  
- ✅ Integração entre dados experimentais e literatura  
- ✅ Estrutura compatível com pipelines de Machine Learning  
- ✅ Extração automatizada de informações via regex  
- ✅ Escalável e adaptável a diferentes domínios biológicos  

---

## Use Case

O framework foi aplicado em um estudo piloto com dados multi-ômicos reais de matrizes de microrganismos, integrando:

- Dados experimentais  
- Dados de literatura  

Os dados foram organizados em formato tabular estruturado, pronto para ingestão em pipelines de IA.

---

## Applications

- Integração de dados multi-ômicos  
- Bioinformática  
- Machine Learning aplicado à biologia  
- Data governance em ciência de dados  
- Estruturação de dados experimentais  

---

## Authors

**Deise Ferreira de Souza**  

  Instituto SENAI de Inovação em Sistemas Embarcados (ISI-SE)  
  
**Jorge Kamassury**

  Instituto SENAI de Inovação em Sistemas Embarcados (ISI-SE)

