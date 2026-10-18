# Challenge: rank it yourself, then check the machine

**40 minutes. Laptops closed for the first half.**

You have built something that turns text into numbers and ranks
documents by how close those numbers sit together. Before you trust it, find out how well it
actually matches your own judgement.

---

## Part One: predict (laptops closed, 15 minutes)

Below are the eight documents already sitting in your index. Read them again, properly this
time, not skimming for code.

For each of the three questions, write down which document you think is the **best** match,
and one sentence on **why**. Do this before looking at anyone else's answers.

**The documents:**

| id | title |
|---|---|
| doc-001 | Harding & Voss - Market Position Note |
| doc-002 | Marchetti Ruiz - Compensation Review |
| doc-003 | Okonkwo Bell - Strategy Briefing |
| doc-004 | Sandoval Kerr - Risk and Compliance Summary |
| doc-005 | Lindqvist Partners - APAC Expansion Review |
| doc-006 | UK Market Commentary - Lateral Hiring |
| doc-007 | Jurisdiction Note - EU Practice Rights |
| doc-008 | Benchmarking Methodology |

*(Full text is in `documents.py` - go and actually read it again rather than working from
the titles alone.)*

**Question 1**
> Which firm works in energy and infrastructure?

My prediction: Okonkwo Bell
Why: Based on the document body: The firm has built a reputation in energy and infrastructure work, particularly projects with a development finance element.

**Question 2**
> Which firms operate in the United States?

My prediction: Marchetti Ruiz
Why: Based on body: The firm's US practice drives the majority of profitability

**Question 3**
> Has any firm had a regulatory or compliance problem recently?

My prediction: Sandoval Kerr 
Why: Sandoval Kerr has invested heavily in its conflicts and compliance function following a difficult period two years ago. The firm's matter intake process now requires sign-off from a dedicated risk partner for any engagement above a defined threshold. Professional indemnity arrangements were renegotiated at the last renewal. There are no outstanding regulatory matters.

---

## Part Two: discuss (10 minutes)

Compare your three answers with the person next to you before opening a laptop. Where did
you agree? Where did you disagree, and why?

---

# PAUSE
### We will come back to this after we implement our endpoint




## Part Three: verify (10 minutes)

Laptops open. Run each of your three questions through the real endpoint:

```bash
curl -X POST http://127.0.0.1:8000/knowledge/search -H "Content-Type: application/json" \
  -d '{"question":"YOUR QUESTION HERE"}'
```

For each one, write down what the machine actually returned as its top result, and its
score.

**Question 1 - machine's top result:** 
Q1. Which firm works in energy and infrastructure?
1. Okonkwo Bell — Strategy Briefing / Score: 0.4445349244383033
2. Harding & Voss — Market Position Note / Score: 0.23587258414890355
3. Sandoval Kerr — Risk and Compliance Summary / Score: 0.20053045608681558

**Did it match your prediction?** Y 

**Question 2 - machine's top result:** 
q. Which firms operate in the United States?
1. Harding & Voss — Market Position Note  score:0.3331372763654285
2. Jurisdiction Note — EU Practice Rights score: 0.2938649929635766
3. Okonkwo Bell — Strategy Briefing score:0.2794320907062965

**Did it match your prediction?** N

**Question 3 - machine's top result:** 
Q. Has any firm had a regulatory or compliance problem recently?
1. Sandoval Kerr — Risk and Compliance Summary / Score: 0.4919565977836593
2. Harding & Voss — Market Position Note / Score: 0.33142967173575705
3. UK Market Commentary — Lateral Hiring / Score: 0.3187299673991228

**Did it match your prediction?** Y

---

## If you finish early

Try these two, same process, no need to write it up formally, just notice what happens:

> What is matter LP-2291?

> What is the position on fixed-share partners?

---

## Keep this sheet

You will want it again this afternoon.
