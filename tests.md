## CLI Manual Tests

**CLI-01**

```bash
python -m app.main --mode generate --task "Объясни теорию графов простыми словами (120–150 слов)" --max-iterations 3 --verbose
```

**CLI-02**

```bash
cat > draft.txt << 'EOF'
наш проект очень крутой потому что он современный и всем нужен. мы сделаем арену где будут компы и люди будут играть и учиться.
EOF
python -m app.main --mode revise --task "Исправь ошибки, сделай научный стиль, добавь структуру" --text-file draft.txt --max-iterations 3 --verbose
```

**CLI-03**

```bash
python -m app.main --mode generate --task "Напиши: Привет." --max-iterations 2 --verbose
```

**CLI-04**

```bash
python -m app.main --mode generate --task "Сформулируй деловое обоснование проекта (220–260 слов)" --max-iterations 1 --verbose
```

**CLI-05**

```bash
python -m app.main --mode generate --task "Объясни что такое машинное обучение" --style "деловой" --max-iterations 2
python -m app.main --mode generate --task "Объясни что такое машинное обучение" --style "учебный" --max-iterations 2
```

**CLI-06**

```bash
python -m app.main --mode revise --task "Сделай текст лучше"
```

**CLI-07**

```bash
python -m app.main --mode generate --task "Напиши краткую актуальность проекта (120 слов)" --max-iterations 2 --report report.json --verbose
cat report.json
```

**CLI-08**

```bash
unset OPENAI_API_KEY
python -m app.main --mode generate --task "Тест" --max-iterations 1
```

---

## Streamlit UI Manual Tests

**UI-01**

```bash
streamlit run ui/streamlit_app.py
```

**UI-02**

* Mode: `generate`
* Task: `Объясни теорию графов простыми словами (120–150 слов)`
* Max iterations: `3`
* Show trace: `ON`
* Run

**UI-03**

* Mode: `revise`
* Task: `Исправь ошибки, сделай научный стиль, добавь структуру`
* Text:
  `наш проект очень крутой потому что он современный и всем нужен. мы сделаем арену где будут компы и люди будут играть и учиться.`
* Show trace: `ON`
* Run

**UI-04**

* Task: *(empty)*
* Run

**UI-05**

* Mode: `revise`
* Task: *(filled)*
* Text: *(empty)*
* Run

**UI-06**

* Mode: `generate`
* Task: `Сделай деловое обоснование проекта (200–250 слов)`
* Max iterations: `1` → Run
* Max iterations: `4` → Run

**UI-07**

* Mode: `generate`
* Task: `Объясни что такое машинное обучение (120–150 слов)`
* Show trace: `OFF`
* Run
