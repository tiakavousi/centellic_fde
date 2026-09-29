# 1. set up some fake building blocks
# 2. create a fake model  (that keeps going)
# 3. sub in our fake in step 2
# 4. hit our endpoint
# 5. check it stopped
# pretend the model never stops ... check your code stops it anyway

class FakeToolUseBlock:
    type = "tool_use",
    id = "toolu_1",
    name = "search_knowledge_base",
    def __init__(self, input_: str):
        self.input = input_

class FakeUsage:
    def __init__(self, i, o):
        self.input_tokens, self.output_tokens = i, o

class FakeResponse:
    def __init__(self, content, stop_reason, usage):
        self.blocks, self.stop_reason, self.usage = content, stop_reason, usage
    
