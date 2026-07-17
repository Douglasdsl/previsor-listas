from pathlib import Path
import re


def carregar_listas(caminho: str):
    linhas = Path(caminho).read_text(encoding="utf-8", errors="ignore").splitlines()
    listas = []

    for numero_linha, linha in enumerate(linhas, start=1):
        nums = [int(x) for x in re.findall(r"\d+", linha)]

        if not nums:
            continue

        if len(nums) != 15:
            raise ValueError(f"Linha {numero_linha}: esperado 15 números, recebido {len(nums)}")

        if any(n < 1 or n > 25 for n in nums):
            raise ValueError(f"Linha {numero_linha}: número fora do intervalo 1..25")

        if len(set(nums)) != 15:
            raise ValueError(f"Linha {numero_linha}: há número repetido na lista")

        listas.append(sorted(nums))

    return listas


def main():
    caminho = "data/raw/listas.txt"
    listas = carregar_listas(caminho)

    print(f"Total de listas válidas: {len(listas)}")
    print(f"Primeira lista: {listas[0]}")
    print(f"Última lista: {listas[-1]}")


if __name__ == "__main__":
    main()
