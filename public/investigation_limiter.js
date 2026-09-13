/**
 * OSINTNeoAI & TaxFunded Investigation Limiter & Session Manager
 * =============================================================
 * Enforces:
 * 1. Maximum 3 concurrent active investigations per user session.
 * 2. Generous daily input allowances (like AI chats) with zero fees required.
 * 3. Immediate local hashing and zero-value ledger pass-through.
 */

class InvestigationSessionManager {
    constructor() {
        this.STORAGE_KEY = "osintneoai_user_session_v1";
        this.MAX_ACTIVE_INVESTIGATIONS = 3;
        this.DAILY_TOKEN_LIMIT = 50000; // Generous 50,000 words/tokens per day
        this.DAILY_SUBMISSION_LIMIT = 100; // Generous 100 zero-fee ledger submissions/day
        this.session = this.loadSession();
    }

    loadSession() {
        const defaultSession = {
            userId: "usr_" + Math.random().toString(36).substring(2, 10),
            createdDate: new Date().toISOString().split("T")[0],
            todayDate: new Date().toISOString().split("T")[0],
            tokensUsedToday: 0,
            submissionsToday: 0,
            activeInvestigations: [
                { id: "INV-001", name: "Primary FCA & Municipal Audit", status: "ACTIVE", created: new Date().toISOString() }
            ],
            ledgerReceipts: []
        };

        try {
            const raw = localStorage.getItem(this.STORAGE_KEY);
            if (!raw) return defaultSession;
            const parsed = JSON.parse(raw);
            
            // Check daily reset
            const today = new Date().toISOString().split("T")[0];
            if (parsed.todayDate !== today) {
                parsed.todayDate = today;
                parsed.tokensUsedToday = 0;
                parsed.submissionsToday = 0;
            }
            return parsed;
        } catch (e) {
            return defaultSession;
        }
    }

    saveSession() {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.session));
        } catch (e) {
            console.error("Failed to save session state:", e);
        }
    }

    canCreateInvestigation() {
        return this.session.activeInvestigations.length < this.MAX_ACTIVE_INVESTIGATIONS;
    }

    createInvestigation(name) {
        if (!this.canCreateInvestigation()) {
            return {
                success: false,
                message: `Active investigation limit reached (${this.MAX_ACTIVE_INVESTIGATIONS} max). Complete or archive an existing investigation to open a new one.`
            };
        }
        const newInv = {
            id: `INV-${Date.now().toString().slice(-4)}`,
            name: name || `Investigation #${this.session.activeInvestigations.length + 1}`,
            status: "ACTIVE",
            created: new Date().toISOString()
        };
        this.session.activeInvestigations.push(newInv);
        this.saveSession();
        return { success: true, investigation: newInv };
    }

    archiveInvestigation(id) {
        this.session.activeInvestigations = this.session.activeInvestigations.filter(inv => inv.id !== id);
        this.saveSession();
        return { success: true };
    }

    canSubmitData(tokenCount = 100) {
        if (this.session.submissionsToday >= this.DAILY_SUBMISSION_LIMIT) {
            return { allowed: false, reason: "Daily submission quota reached. Resets at midnight UTC." };
        }
        if (this.session.tokensUsedToday + tokenCount > this.DAILY_TOKEN_LIMIT) {
            return { allowed: false, reason: "Daily input token buffer exceeded. Resets at midnight UTC." };
        }
        return { allowed: true };
    }

    recordSubmission(receiptHash, text) {
        const estimatedTokens = Math.ceil(text.length / 4);
        this.session.submissionsToday += 1;
        this.session.tokensUsedToday += estimatedTokens;
        this.session.ledgerReceipts.push({
            hash: receiptHash,
            timestamp: new Date().toISOString(),
            value: 0
        });
        this.saveSession();
    }

    getStats() {
        return {
            activeInvestigationsCount: this.session.activeInvestigations.length,
            maxInvestigations: this.MAX_ACTIVE_INVESTIGATIONS,
            tokensUsedToday: this.session.tokensUsedToday,
            dailyTokenLimit: this.DAILY_TOKEN_LIMIT,
            submissionsToday: this.session.submissionsToday,
            dailySubmissionLimit: this.DAILY_SUBMISSION_LIMIT,
            activeInvestigations: this.session.activeInvestigations
        };
    }
}

if (typeof window !== "undefined") {
    window.InvestigationManager = new InvestigationSessionManager();
}
