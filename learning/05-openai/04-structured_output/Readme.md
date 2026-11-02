# Structured Output

- `EmailReview` Pydantic model email review ka output fixed fields mein rakhta hai: professional hai ya nahi, sentences ki tadaad, aur personalization placeholders.
- Checker agent email ko review karke isi structure mein result deta hai.
- `email_checker()` structured result par rules lagata hai: unprofessional email ya placeholders hoon to reject, warna good.
- `Runner.run()` agent chalata hai; `final_output` se validated review lekar final decision print hota hai.

**Flow:** Email → Checker agent → `EmailReview` → rule check → decision.
