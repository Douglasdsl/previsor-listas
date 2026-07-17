# Aplicação Fase 5D-R4

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5d-r4.zip
chmod +x scripts/aplicar_fase5d_r4.sh
./scripts/aplicar_fase5d_r4.sh
```

Teste obrigatório:

1. Abrir `/metodos`.
2. Fazer hard refresh: `Ctrl+F5`.
3. Colar a lista real no campo cego.
4. Clicar em `Pontuar localmente sem enviar ao backend`.
5. Conferir coluna de notas.
6. Conferir preenchimento do relatório.
7. Clicar em `Copiar relatório sem números`.
8. Clicar em `Enviar somente pontuações ao backend`.
9. Conferir `/feedback-resumo`.

Versionar:

```bash
git add src/api.py src/feedback.py static/metodos.js scripts/aplicar_fase5d_r4.sh reports/fase5d_r4_refatoracao_estavel_front.md README_FASE5D_R4_APLICAR.md
git commit -m "fase-5d-r4-refatora-front-feedback-estavel"
git push
```
