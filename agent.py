import google.generativeai as genai
from uagents import Agent, Context, Protocol, Model, Field
from ai_engine import UAgentResponse, UAgentResponseType

# Initialize the agent
agent = Agent()

# Configure the Google Gemini API with your API key
genai.configure(api_key="")  # Replace with your actual API key

# Define the protocol for handling blog requests
blog_protocol = Protocol(name="BlogRequestProtocol")

# Define the model for blog requests
class BlogRequest(Model):
    blog_topic: str = Field(description="The topic of the blog content.")

# Function to get blog content from Google Gemini API
async def get_blog_content(blog_topic: str) -> dict:
    try:
        # Initialize the model and generate content
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(blog_topic)  # Send the blog topic directly as a prompt
        return {"output": response.text}
    except Exception as e:
        return {"error": str(e), "message": "An error occurred while calling the Gemini API."}

# Define the message handler for blog requests
@blog_protocol.on_message(model=BlogRequest, replies={UAgentResponse})
async def handle_blog_request(ctx: Context, sender: str, msg: BlogRequest):
    ctx.logger.info(f"Received blog request for topic: '{msg.blog_topic}'")
    
    # Print the received request
    print(f"**Received Blog Request**:\n\n- **Topic**: {msg.blog_topic}\n")

    try:
        # Fetch blog content from Google Gemini API
        response = await get_blog_content(msg.blog_topic)
        ctx.logger.info(f"Response from Google Gemini API: {response}")
        
        # Check if there was an error in the response
        if 'error' in response:
            print(f"**Error**:\n\n- **Message**: {response['message']}\n")
            message = f"Error generating blog content: {response['message']}"
        else:
            blog_content = response.get("output", "Unable to generate content.")
            print(f"**Generated Blog Content**:\n\n{blog_content}\n")
            message = blog_content if blog_content else "No content was generated for the given topic."

    except Exception as e:
        ctx.logger.error(f"An error occurred while generating blog content: {e}")
        message = f"An unexpected error occurred: {e}"
        
        # Print the error
        print(f"**Unexpected Error**:\n\n- **Error**: {e}\n")

    # Send the generated blog content back to the user
    await ctx.send(sender, UAgentResponse(message=message, type=UAgentResponseType.FINAL))

# Include the protocol and run the agent
agent.include(blog_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
