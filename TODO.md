# TODO: Modify AI to Answer Random Eco-Related Questions

## Tasks
- [x] Modify `ai_service.py`: Update `generate_advice` method to handle general eco-related questions, not just activity-specific advice.
- [x] Modify `app/routes/ai.py`: Adjust `/chat` endpoint to pass the full message to AI without strict activity parsing, allowing broader eco questions.
- [x] Test the changes by running the app and sending various eco-related questions to `/api/ai/chat`.

## Notes
- Keep the AI focused on eco-related topics.
- If activity details are detected, provide personalized advice; otherwise, answer general eco questions.
- Ensure fallback works if OpenAI API is unavailable.
