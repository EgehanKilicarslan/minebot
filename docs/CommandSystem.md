# Command Configuration Guide

This document explains the command configuration system used in our Discord bot. Let's break down the configuration structure using the "ban" command as an example.

## Command Configuration Structure

Each command in the bot is configured through a JSON structure that determines its behavior, permissions, cooldowns, and logging features. Here's a detailed explanation of each component:

### Basic Structure

```json
"ban": {
    "enabled": true,
    "permissions": ["BAN_MEMBERS"],
    "cooldown": {
        "algorithm": "fixed_window",
        "bucket": "user",
        "window_length": 60,
        "allowed_invocations": 1
    },
    "log": {
        "enabled": true,
        "channel": 1163899262044745790
    }
}
```

### Components Explained

#### Command Activation

```json
"enabled": true
```
- **Purpose**: Controls whether the command is active in the bot
- **Values**: `true` (command is available) or `false` (command is disabled)
- **Usage**: Quickly enable or disable commands without removing their configuration

#### Permissions

```json
"permissions": ["BAN_MEMBERS"]
```
- **Purpose**: Defines what Discord permissions users need to execute this command
- **Values**: Any valid Discord permission (e.g., `"BAN_MEMBERS"`, `"KICK_MEMBERS"`, `"ADMINISTRATOR"`)
- **Special Value**: `"NONE"` allows anyone to use the command
- **Multiple Permissions**: Specify multiple permissions in the array if needed
- **Behavior**: Users must have ALL listed permissions to use the command
- **Default**: If the permissions section is omitted, it defaults to `"NONE"` (anyone can use the command)

#### Cooldown System

```json
"cooldown": {
    "algorithm": "fixed_window",
    "bucket": "user",
    "window_length": 60,
    "allowed_invocations": 1
}
```

- **Purpose**: Prevents spam by limiting how often a command can be used
- **Components**:
  - `algorithm`: How the cooldown is calculated
    - `fixed_window`: Resets after a fixed time period
    - `sliding_window`: Continuously moves the time window
  - `bucket`: What the cooldown applies to
    - `user`: Individual users have separate cooldowns
    - `channel`: Cooldown applies to all users in a channel
    - `guild`: Cooldown applies to the entire server
    - `global`: Cooldown applies across all servers
  - `window_length`: Time period in seconds
  - `allowed_invocations`: Number of uses allowed within the time period
- **Default**: If the entire cooldown section is omitted, the command will have no cooldown restrictions

#### Command Logging

```json
"log": {
    "enabled": true,
    "channel": 1163899262044745790
}
```

- **Purpose**: Records command usage for moderation and audit purposes
- **Components**:
  - `enabled`: Whether logging is active for this command
  - `channel`: The Discord channel ID where logs will be sent
- **Note**: If `log.enabled` is set to `false`, the `channel` property becomes optional and can be removed

## Real-World Example

For the ban command shown above:

1. **Status**: The command is active and available for use
2. **Permissions**: Only users with the "Ban Members" permission can use this command
3. **Cooldown**: Users can only use this command once every 60 seconds
4. **Logging**: Every use of the ban command will be logged to the specified channel

## Optional Configuration and Defaults

You can simplify command configurations by omitting certain sections when default behavior is desired:

```json
"simple-command": {
    "enabled": true
}
```

This minimal configuration:
- Enables the command
- Sets permissions to `"NONE"` (anyone can use it)
- Has no cooldown restrictions
- Has logging disabled

## Benefits of This Configuration System

- **Granular Control**: Each command can have its own unique settings
- **Easy Maintenance**: Quickly adjust settings without modifying code
- **Security**: Proper permission controls prevent unauthorized use
- **Anti-Spam**: Cooldown system prevents command abuse
- **Accountability**: Logging system creates an audit trail for moderation actions
- **Flexibility**: Use only the configuration sections you need

For administrators, this configuration can be modified in the settings.json file to adjust behavior according to your server's specific needs.