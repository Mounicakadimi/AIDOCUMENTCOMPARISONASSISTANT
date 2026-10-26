
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from document_reader import extract_pdf_text
from comparison import compare_documents
from report_generator import build_report
from io import BytesIO

app = FastAPI(title="AI Document Comparison Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Document Comparison Assistant</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f5fb;
    color: #20243a;
}
header {
    background: linear-gradient(120deg, #4338ca, #7c3aed);
    color: white;
    text-align: center;
    padding: 38px 20px;
}
header h1 { margin: 0 0 12px; }
header p { margin: 0; }
main { max-width: 1000px; margin: 30px auto; padding: 0 18px; }
.uploads {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}
.card, .result {
    background: white;
    padding: 24px;
    border-radius: 14px;
    box-shadow: 0 5px 20px #20243a0d;
    margin-bottom: 20px;
}
.upload-box {
    border: 2px dashed #a5a8d6;
    padding: 25px 15px;
    border-radius: 10px;
    text-align: center;
}
input[type=file] { max-width: 100%; margin-top: 15px; }
button, .download {
    border: 0;
    border-radius: 9px;
    padding: 13px 20px;
    background: #5145cd;
    color: white;
    cursor: pointer;
    font-weight: bold;
    text-decoration: none;
    display: inline-block;
}
button:hover, .download:hover { background: #392fa8; }
#compareBtn { width: 100%; margin: 22px 0; }
#status { margin: 15px 0; white-space: pre-wrap; }
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
}
.metric {
    background: #f0efff;
    padding: 18px;
    border-radius: 10px;
}
.metric strong { display: block; font-size: 24px; margin-top: 8px; }
pre {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    background: #f7f7fb;
    padding: 16px;
    border-radius: 8px;
}
section { margin-top: 25px; }
h2 { color: #4338ca; }
.hidden { display: none; }
footer { text-align: center; padding: 25px; color: #6b7280; }
</style>
</head>
<body>
<header>
    <h1>AI Document Comparison Assistant</h1>
    <p>Upload two PDF documents to discover similarities and differences.</p>
</header>

<main>
    <div class="uploads">
        <div class="card">
            <h3>Document A</h3>
            <div class="upload-box">
                <p>Choose your first PDF document</p>
                <input id="fileA" type="file" accept=".pdf,application/pdf">
            </div>
        </div>
        <div class="card">
            <h3>Document B</h3>
            <div class="upload-box">
                <p>Choose your second PDF document</p>
                <input id="fileB" type="file" accept=".pdf,application/pdf">
            </div>
        </div>
    </div>

    <button id="compareBtn" onclick="compareFiles()">
        Compare Documents
    </button>
    <div id="status" role="status"></div>

    <div id="results" class="result hidden">
        <h2>Comparison Results</h2>
        <div id="metrics" class="metric-grid"></div>

        <section>
            <h2>Document A Summary</h2>
            <p id="summaryA"></p>
        </section>

        <section>
            <h2>Document B Summary</h2>
            <p id="summaryB"></p>
        </section>

        <section>
            <h2>Comparison Analysis</h2>
            <p id="analysis"></p>
        </section>

        <section>
            <h2>Shared Words</h2>
            <pre id="shared"></pre>
        </section>

        <section>
            <h2>Words Only in Document A</h2>
            <pre id="onlyA"></pre>
        </section>

        <section>
            <h2>Words Only in Document B</h2>
            <pre id="onlyB"></pre>
        </section>

        <section>
            <h2>Text Differences</h2>
            <pre id="diff"></pre>
        </section>

        <button onclick="downloadReport()">Download Report</button>
    </div>
</main>

<footer>AI Document Comparison Assistant</footer>

<script>
let latestResult = null;

function showText(id, value) {
    document.getElementById(id).textContent =
        value === null || value === undefined || value === ""
        ? "No information available."
        : String(value);
}

function formatWords(words) {
    if (Array.isArray(words)) {
        return words.length ? words.join(", ") : "None found.";
    }
    return words || "None found.";
}

async function compareFiles() {
    const fileA = document.getElementById("fileA").files[0];
    const fileB = document.getElementById("fileB").files[0];
    const status = document.getElementById("status");
    const results = document.getElementById("results");
    const button = document.getElementById("compareBtn");

    results.classList.add("hidden");
    latestResult = null;

    if (!fileA || !fileB) {
        status.textContent = "Please select both PDF documents.";
        return;
    }

    if (!fileA.name.toLowerCase().endsWith(".pdf") ||
        !fileB.name.toLowerCase().endsWith(".pdf")) {
        status.textContent = "Only PDF files are accepted.";
        return;
    }

    status.textContent = "Reading and comparing documents...";
    button.disabled = true;

    try {
        const form = new FormData();
        form.append("file_a", fileA);
        form.append("file_b", fileB);

        const response = await fetch("/compare", {
            method: "POST",
            body: form
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Comparison failed.");
        }

        latestResult = data;

        const metrics = data.metrics || {};
        document.getElementById("metrics").innerHTML = "";

        const metricItems = [
            ["Similarity", (metrics.similarity_percent ?? 0) + "%"],
            ["Words in A", metrics.words_a ?? 0],
            ["Words in B", metrics.words_b ?? 0],
            ["Shared Words", metrics.shared_word_count ?? 0]
        ];

        for (const item of metricItems) {
            const box = document.createElement("div");
            box.className = "metric";
            const label = document.createElement("span");
            label.textContent = item[0];
            const value = document.createElement("strong");
            value.textContent = item[1];
            box.append(label, value);
            document.getElementById("metrics").appendChild(box);
        }

        showText("summaryA", data.summary_a);
        showText("summaryB", data.summary_b);
        showText("analysis", data.analysis);
        showText("shared", formatWords(data.shared_words));
        showText("onlyA", formatWords(data.words_a));
        showText("onlyB", formatWords(data.words_b));
        showText("diff", data.diff);

        results.classList.remove("hidden");
        status.textContent = "Comparison completed successfully.";
    } catch (error) {
        status.textContent = "Error: " + error.message +
            "\\nPlease check your PDFs and try again.";
    } finally {
        button.disabled = false;
    }
}

function downloadReport() {
    if (!latestResult || !latestResult.report) {
        document.getElementById("status").textContent =
            "No report is available. Compare the documents first.";
        return;
    }

    const blob = new Blob([latestResult.report], {
        type: "text/plain;charset=utf-8"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "document_comparison_report.txt";
    link.click();
    URL.revokeObjectURL(url);
}
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE


@app.post("/compare")
async def compare(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...)
):
    max_size = 15 * 1024 * 1024

    try:
        documents = []

        for uploaded in (file_a, file_b):
            if not uploaded.filename or not uploaded.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail="Please upload PDF files only."
                )

            content = await uploaded.read()

            if not content:
                raise HTTPException(
                    status_code=400,
                    detail=f"{uploaded.filename} is empty."
                )

            if len(content) > max_size:
                raise HTTPException(
                    status_code=413,
                    detail="Each PDF must be 15 MB or smaller."
                )

            if not content.startswith(b"%PDF-"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{uploaded.filename} is not a valid PDF."
                )

            text = extract_pdf_text(content)
            documents.append(text)

        text_a, text_b = documents

        result = compare_documents(text_a, text_b)

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="The comparison module returned an unexpected result."
            )

        result["words_a"] = result.get("words_a", [])
        result["words_b"] = result.get("words_b", [])
        result["shared_words"] = result.get("shared_words", [])

        report = build_report(
            file_a.filename,
            file_b.filename,
            result
        )

        return JSONResponse({
            "summary_a": result.get("summary_a", ""),
            "summary_b": result.get("summary_b", ""),
            "analysis": result.get("analysis", result.get("comparison", "")),
            "shared_words": result.get("shared_words", []),
            "words_a": result.get("words_a", []),
            "words_b": result.get("words_b", []),
            "diff": result.get("diff", ""),
            "metrics": {
                "similarity_percent": result.get("similarity_percent", 0),
                "words_a": result.get("word_count_a", len(text_a.split())),
                "words_b": result.get("word_count_b", len(text_b.split())),
                "shared_word_count": len(result.get("shared_words", []))
            },
            "report": report
        })

    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not compare the documents: {error}"
        )
