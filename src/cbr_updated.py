import cbrkit
from cbrkit.retrieval import build, dropout, apply_query
import pandas as pd
import tempfile
import os

class Cbr():
    def __init__(self):
        self.indice = 0
        self.casos = self.atualizarDataframe()

    def atualizarDataframe(self):
        # Carrega o CSV original e trata os "NULL"
        # O arquivo está no diretório pai, não no diretório atual
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dbtrucoimitacao_maos.csv")
        df = pd.read_csv(path, na_values=["NULL"])

        if 'segundaCartaHumano' in df.columns:
            df['segundaCartaHumano'] = pd.to_numeric(df['segundaCartaHumano'], errors='coerce')
        df = df.fillna(0)

        df.replace('ESPADAS', '1', inplace=True)
        df.replace('OURO', '2', inplace=True)
        df.replace('BASTOS', '3', inplace=True)
        df.replace('COPAS', '4', inplace=True)

        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].astype('int').apply(abs)

        # Salva o dataframe limpo em um arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            temp_csv = tmp.name
            df.to_csv(temp_csv, index=False)

        # Carrega o arquivo limpo usando o cbrkit
        df_cleaned = cbrkit.loaders.file(temp_csv)

        # Remove o arquivo temporário
        os.remove(temp_csv)

        #print(list(df_cleaned.values()))
        return df_cleaned
    
    def buscarSimilares(self, registro: dict) -> list[dict]:
        # Filtra o registro apenas com as chaves presentes (que representam as rodadas já obtidas)
        registro_filtrado = {k: v for k, v in registro.items()}
        useful_columns = list(registro_filtrado.keys())
        # Converte os casos para DataFrame apenas com as colunas úteis
        df_casos = pd.DataFrame([
            case.to_dict() if hasattr(case, "to_dict") else dict(case)
            for case in self.casos.values()
        ])
        df_casos_filtrado = df_casos[useful_columns].copy()
        
        # Calcular funções de similaridade dinamicamente para cada coluna útil
        attr_sims = {}
        for col in useful_columns:
            if pd.api.types.is_numeric_dtype(df_casos_filtrado[col]):
                mn = df_casos_filtrado[col].min()
                mx = df_casos_filtrado[col].max()
                if mx == mn:
                    attr_sims[col] = lambda x, y, a=col: 1.0 if x == y else 0.0
                else:
                    attr_sims[col] = cbrkit.sim.numbers.linear_interval(mn, mx)
            else:
                attr_sims[col] = lambda x, y: 1.0 if x == y else 0.0
        
        # Calcula a similaridade global usando cbrkit para os campos disponíveis
        global_sim = cbrkit.sim.attribute_value(
            attributes=attr_sims,
            aggregator=cbrkit.sim.aggregator("mean")
        )
        retriever = build(global_sim)
        limited_ret = dropout(retriever, limit=100, min_similarity=0.9)
        result = apply_query(self.casos, registro_filtrado, limited_ret)
        
        # Filtra e retorna apenas os casos com similaridade >= 0.8
        similares = []
        for case_id, score in zip(result.ranking, result.similarities):
            raw = self.casos[case_id]
            c = raw.to_dict() if hasattr(raw, "to_dict") else dict(raw)
            if score >= 0.8:
                c["_sim_score"] = score
                similares.append(c)
        return similares

