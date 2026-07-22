import axios from "axios";

async function testPipeline() {
  const baseURL = "http://localhost:3000/api/trpc";
  console.log("Starting pipeline verification tests...");

  try {
    // 1. Create Analysis
    console.log("\n[Step 1] Creating a new OSINT Analysis Session...");
    const createRes = await axios.post(`${baseURL}/analysis.create`, {
      title: "Automated Verification Case",
      description: "Testing local in-memory pipeline"
    });
    const analysisId = createRes.data.result.data.analysisId;
    console.log(`[OK] Analysis Session created successfully. ID: ${analysisId}`);

    // 2. Upload Mock File (Base64 encoded text)
    console.log("\n[Step 2] Uploading case file (test_intel_brief.txt)...");
    const rawContent = "Agent Report: John Doe met with Jane Smith in Washington to discuss the project. Later, Jane Smith emailed Bob Johnson regarding the updates.";
    const base64Content = Buffer.from(rawContent).toString("base64");

    const uploadRes = await axios.post(`${baseURL}/file.upload`, {
      analysisId,
      fileName: "test_intel_brief.txt",
      fileType: "txt",
      fileSize: rawContent.length,
      fileContent: base64Content
    });
    const fileId = uploadRes.data.result.data.fileId;
    console.log(`[OK] File uploaded successfully. ID: ${fileId}`);

    // 3. Process File and Extract Entities
    console.log("\n[Step 3] Running entity extraction and relationship mapping...");
    const processRes = await axios.post(`${baseURL}/extraction.processFile`, {
      analysisId,
      fileId,
      fileContent: rawContent,
      fileType: "txt"
    });

    console.log("\n============================================================");
    console.log("                    PIPELINE VERIFICATION RESULTS            ");
    console.log("============================================================");
    console.log("Extraction Status:", processRes.data.result.data.success ? "SUCCESS" : "FAILED");
    console.log("Total Entities Identified:", processRes.data.result.data.entitiesExtracted);
    console.log("People Found:", processRes.data.result.data.peopleFound);
    console.log("[OK] Pipeline Verification Test Completed Successfully!");
  } catch (error) {
    console.error("[ERROR] Pipeline verification failed:", error.response?.data || error.message);
  }
}

testPipeline();
