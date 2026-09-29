## Objectives of firm intelligence API:
- Ability to generate an index for firm documents
- Ability to query a database of ocuments
- Ability to trace the documents that were used to generate an answer
- Ability to see the cost of any given call to the model
- Ability to refuse an answer when nothing relevant exists (rather than model hussing the answer)
- Ability to retry safely (without creating duplicate records - idempotency)
- Ability to let the model decide for itself whether it needs to search ... rather than always searching
- Ability to generate a validated structured analysis of a firm
- Ability to steam a response as its being generated rather than waiting for the whole thing to finish
- Ability to prove the service still runs/behaves correctly after a change ... automatically


### Part 0 - : 
- setup venv with required dependencies

### Part 1 - :
- 8 documents sitting in a file ... each has an id, title plus a block of text
- someone triggers indexing ... one off requests that tells the service "read all of this now"
- we start by reading just the text of each documents ready to send off

### Part 2 - Turning the documents into numbers:
- All texts are sent together, single request to Voyage
- Voyage reads each one and truns it into a list of numbers representing what it means
- 8 list of numbers (one per doc) how many tokens that cost

### Part 3 - Storing them:
- Each docs numbers get handed to Chroma (plus id and the original text)
- Chroma saves all of to disk (our data persistence)
- NOTE: nothing can be searched until this step has actially happend once

### Part 4 - A question comes in:
- User sends a question to the service
- We trigger relevant function at the endpoint with validatiosn (length check , etc)
- An invalid question gets rejected strainght away - nothing else would run

### Part 5 - The question becomes a vector:
- the question's text gets sent to Voyageai (same as the docs)
- It comes back as a list of numbers (the same shape as the docs)

### Part 6 - Finding the closest documents:
- The question's numbers get compared against every docs numbers that are already in Croma
- NOTE - this comparison measures how close each doc is the questions (it does this in meaning not wording)
- The closes few come back (ranked and carrying score)

### Part 7 - Decide whether its worth answering
- Each returned docs score gets checked against our RELEVANCE_FLOOR
- Anything that dosn't clear the bar gets thrown away
- If nothing clears the bar ... our service stops here, says it can't answer no further action

### Part 8 - Preparing what the model will see:
- The docs that did clear the bar get combined into one block of text
    - each one keeps its id and title attached (so it can be referenced / pointed back to later)
- That block, plus original question is All the model knows (GROUNDED)

### Part 9 - Getting an answer:
- That block and the question get sent to Anthropic
- The SYSTEM_PROMPT tells the model ahead of time that it can only use what its given
- It reads everything it was given and writes a response
    - in the response it marks which document each part of the answer came from

### Part 10 - Sending the answer back:
- Answer comes back along with how much was spent
    - input_tokens, output_tokens, stop_reason
- The service assembles the final response (answer which doc were used , how relevant each one was, and what it cost)
- Response goes back to whoever asked the original question.




