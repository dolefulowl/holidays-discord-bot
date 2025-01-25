import discord
from db import list_users, set_gc

users = list_users()

# Modal with a Text Input Field
class CongratulationForm(discord.ui.Modal, title="Congratulation Form"):
    feedback_text = discord.ui.TextInput(
        label="Congratulations",
        style=discord.TextStyle.paragraph,
        placeholder="Type your warm words here...",
        required=True,
        max_length=500,
    )

    def __init__(self, selected_option, user_id):
        super().__init__()
        self.selected_option = selected_option
        self.user_id = user_id
        self.selected_index = next((i for i, user in enumerate(users) if user[1] == self.selected_option), None)

    async def on_submit(self, interaction: discord.Interaction):

        try:
            set_gc(
                sender_discord_id=self.user_id,
                receiver_discord_id=users[self.selected_index][0],
                message=self.feedback_text.value
            )
            await interaction.response.send_message(f'Celebration added for {self.selected_option}!', ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f'Failed to add celebration for {self.selected_option} (((', ephemeral=True)
            raise e


# Dropdown for Selecting Feedback Type
class CongratulationDropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=user[1],description=user[2]) for user in users]
        super().__init__(
            placeholder="Choose your pokemon...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Trigger the modal with the selected option
        selected_option = self.values[0]

        user_id = interaction.user.id  # Get the user's Discord ID
        modal = CongratulationForm(selected_option, user_id)
        await interaction.response.send_modal(modal)


# View with Dropdown
class CongratulationView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(CongratulationDropdown())
