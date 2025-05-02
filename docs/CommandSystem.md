# 🛠️ Command Configuration Guide

This document explains the command configuration system used in our Discord bot. We'll break down the structure using the "ban" command as an example.

## 📋 Command Configuration Structure

Each command is configured through a JSON structure that determines its behavior, permissions, cooldowns, and logging features.

### ✨ Basic Structure

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

## 🧩 Components Explained

### Command Activation

```json
"enabled": true
```

| Property  | Purpose                                | Values            | Default        |
| --------- | -------------------------------------- | ----------------- | -------------- |
| `enabled` | Controls whether the command is active | `true` or `false` | N/A (required) |

- **Usage**: Quickly enable or disable commands without removing their configuration

### Permissions

```json
"permissions": ["BAN_MEMBERS"]
```

| Property      | Purpose                              | Values                       | Default    |
| ------------- | ------------------------------------ | ---------------------------- | ---------- |
| `permissions` | Defines required Discord permissions | Any valid Discord permission | `["NONE"]` |

- **Special Value**: `"NONE"` allows anyone to use the command
- **Multiple Permissions**: Specify multiple permissions in the array if needed
- **Behavior**: Users must have ALL listed permissions to use the command

### Cooldown System

```json
"cooldown": {
    "algorithm": "fixed_window",
    "bucket": "user",
    "window_length": 60,
    "allowed_invocations": 1
}
```

| Property              | Purpose                    | Values                               | Default        |
| --------------------- | -------------------------- | ------------------------------------ | -------------- |
| `algorithm`           | How cooldown is calculated | `fixed_window`, `sliding_window`     | N/A (required) |
| `bucket`              | What cooldown applies to   | `user`, `channel`, `guild`, `global` | N/A (required) |
| `window_length`       | Time period in seconds     | Integer value                        | N/A (required) |
| `allowed_invocations` | Uses allowed within period | Integer value                        | N/A (required) |

- **Algorithm Types**:

  - `fixed_window`: Resets after a fixed time period
  - `sliding_window`: Continuously moves the time window

- **Bucket Types**:
  - `user`: Individual users have separate cooldowns
  - `channel`: Cooldown applies to all users in a channel
  - `guild`: Cooldown applies to the entire server
  - `global`: Cooldown applies across all servers

### Command Logging

```json
"log": {
    "enabled": true,
    "channel": 1163899262044745790
}
```

| Property  | Purpose                            | Values                   | Default                   |
| --------- | ---------------------------------- | ------------------------ | ------------------------- |
| `enabled` | Controls whether logging is active | `true` or `false`        | `false`                   |
| `channel` | Channel ID for logs                | Valid Discord channel ID | N/A (required if enabled) |

- **Note**: If `log.enabled` is `false`, the `channel` property becomes optional

## 🔍 Real-World Example

For the ban command shown above:

1. ✅ **Status**: The command is active and available for use
2. 🔒 **Permissions**: Only users with the "Ban Members" permission can use this command
3. ⏱️ **Cooldown**: Users can only use this command once every 60 seconds
4. 📝 **Logging**: Every use of the ban command will be logged to the specified channel

## 🧰 Optional Configuration and Defaults

You can simplify command configurations by omitting certain sections when default behavior is desired:

```json
"simple-command": {
    "enabled": true
}
```

This minimal configuration:

- ✅ Enables the command
- 🔓 Sets permissions to `"NONE"` (anyone can use it)
- 🕒 Has no cooldown restrictions
- 📵 Has logging disabled

## 💡 Benefits of This Configuration System

| Benefit              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| **Granular Control** | Each command can have its own unique settings                |
| **Easy Maintenance** | Quickly adjust settings without modifying code               |
| **Security**         | Proper permission controls prevent unauthorized use          |
| **Anti-Spam**        | Cooldown system prevents command abuse                       |
| **Accountability**   | Logging system creates an audit trail for moderation actions |
| **Flexibility**      | Use only the configuration sections you need                 |

For administrators, this configuration can be modified in the `settings.json` file to adjust behavior according to your server's specific needs.

## 📚 Configuration Cheat Sheet

```json
{
  "command-name": {
    "enabled": true|false,                  // Required
    "permissions": ["PERM1", "PERM2"],      // Optional, defaults to ["NONE"]
    "cooldown": {                          // Optional, no cooldown if omitted
      "algorithm": "fixed_window|sliding_window",
      "bucket": "user|channel|guild|global",
      "window_length": 60,                 // Time in seconds
      "allowed_invocations": 5             // Number of allowed uses
    },
    "log": {                               // Optional, no logging if omitted
      "enabled": true|false,
      "channel": 1234567890123456789       // Discord channel ID
    }
  }
}
```
