import hikari
import lightbulb

from data_types import TimedDict, TimedSet


class BotState:
    """Manages the Discord bot client state."""

    _bot: hikari.GatewayBot | None = None
    _client: lightbulb.Client | None = None
    _member: hikari.Member | None = None

    @staticmethod
    def set_bot(bot: hikari.GatewayBot) -> None:
        """Set the Hikari bot instance."""
        BotState._bot = bot

    @staticmethod
    def get_bot() -> hikari.GatewayBot:
        """Get the Hikari bot instance."""
        if BotState._bot is None:
            raise ValueError("Bot has not been set.")
        return BotState._bot

    @staticmethod
    def set_client(client: lightbulb.Client) -> None:
        """Set the Lightbulb client instance."""
        BotState._client = client

    @staticmethod
    def get_client() -> lightbulb.Client:
        """Get the Lightbulb client instance."""
        if BotState._client is None:
            raise ValueError("Client has not been set.")
        return BotState._client

    @staticmethod
    def set_member(member: hikari.Member) -> None:
        """Set the bot's member instance."""
        BotState._member = member

    @staticmethod
    def get_member() -> hikari.Member:
        """Get the bot's member instance."""
        if BotState._member is None:
            raise ValueError("Member has not been set.")
        return BotState._member


class GuildState:
    _locale: hikari.Locale | None = None
    _booster_role: hikari.Role | None = None

    @staticmethod
    def set_locale(locale: hikari.Locale) -> None:
        """Set the locale for the guild."""
        GuildState._locale = locale

    @staticmethod
    def get_locale() -> hikari.Locale:
        """Get the locale for the guild."""
        if GuildState._locale is None:
            raise ValueError("Locale has not been set.")
        return GuildState._locale

    @staticmethod
    def set_booster_role(role: hikari.Role | None) -> None:
        """Set the booster role for the guild."""
        GuildState._booster_role = role

    @staticmethod
    def get_booster_role() -> hikari.Role | None:
        """Get the booster role for the guild."""
        return GuildState._booster_role


class MinecraftState:
    """Manages Minecraft-related state data."""

    _minecraft_servers: list[str] = []
    _online_players: TimedSet[str] = TimedSet[str](10)
    _player_uuids: TimedDict[str, str] = TimedDict[str, str](10)
    _player_servers: TimedDict[str, str] = TimedDict[str, str](10)

    @staticmethod
    def add_server(servers: str | list[str]) -> None:
        """Add Minecraft server(s) to the list."""
        if isinstance(servers, str):
            MinecraftState._minecraft_servers.append(servers)
        else:
            MinecraftState._minecraft_servers.extend(servers)

    @staticmethod
    def get_servers() -> list[str]:
        """Get the list of Minecraft servers."""
        return (
            MinecraftState._minecraft_servers.copy()
        )  # Return a copy to prevent external modification

    @staticmethod
    def contains_server(server: str) -> bool:
        """Check if a Minecraft server is in the list."""
        return server in MinecraftState._minecraft_servers

    @staticmethod
    def clear_servers() -> None:
        """Clear the list of Minecraft servers."""
        MinecraftState._minecraft_servers.clear()

    @staticmethod
    def add_online_player(player: str) -> None:
        """Add a player to the online players set."""
        MinecraftState._online_players.add(player)

    @staticmethod
    def check_player_online(player: str) -> bool:
        """Check if a player is online."""
        return MinecraftState._online_players.contains(player)

    @staticmethod
    def add_player_uuid(username: str, uuid: str) -> None:
        """Add a player's UUID to the dictionary."""
        MinecraftState._player_uuids[username] = uuid

    @staticmethod
    def get_player_uuid(username: str) -> str | None:
        """Get a player's UUID by username."""
        return MinecraftState._player_uuids.get(username)

    @staticmethod
    def add_player_server(username: str, server: str) -> None:
        """Add a player's server to the dictionary."""
        MinecraftState._player_servers[username] = server

    @staticmethod
    def get_player_server(username: str) -> str | None:
        """Get a player's server by username."""
        return MinecraftState._player_servers.get(username)


class GlobalState:
    """Global state manager for the bot."""

    bot: BotState = BotState()
    guild: GuildState = GuildState()
    minecraft: MinecraftState = MinecraftState()
