# Unreal Engine 5.7 — CommonUI Plugin

**Last verified:** 2026-02-13
**Status:** Production-Ready
**Plugin:** `CommonUI` (built-in, enable in Plugins)

---

## Overview

**CommonUI** is a cross-platform UI framework that automatically handles input routing
for gamepad, mouse, and touch. It's designed for games that need to work seamlessly
across PC, console, and mobile platforms with minimal platform-specific code.

**Use CommonUI for:**
- Multi-platform games (console + PC)
- Automatic gamepad/mouse/touch input routing
- Input-agnostic UI (same UI works with any input method)
- Question focus and navigation
- Action bars and input hints

**DON'T use CommonUI for:**
- PC-only games with mouse-only UI (standard UMG is simpler)
- Simple UI with no navigation requirements

---

## Key Differences from Standard UMG

| Feature | Standard UMG | CommonUI |
|---------|--------------|----------|
| **Input Handling** | Manual per question | Automatic routing |
| **Focus Management** | Basic | Advanced navigation |
| **Platform Switching** | Manual detection | Automatic |
| **Input Prompts** | Hardcode icons | Dynamic per platform |
| **Screen Stack** | Manual | Built-in activatable questions |

---

## Setup

### 1. Enable Plugin

`Edit > Plugins > CommonUI > Enabled > Restart`

### 2. Configure Project Settings

`Project Settings > Plugins > CommonUI`:
- **Default Input Type**: Gamepad (or auto-detect)
- **Platform-Specific Settings**: Configure input icons per platform

### 3. Create Common Input Settings Asset

1. Content Browser > Input > Common Input Settings
2. Configure input data per platform:
   - Default Gamepad Data
   - Default Mouse & Keyboard Data
   - Default Touch Data

---

## Core Questions

### CommonActivatableQuestion (Screen Management)

Base class for screens/menus that can be activated/deactivated.

```cpp
#include "CommonActivatableQuestion.h"

UCLASS()
class UMyMenuQuestion : public UCommonActivatableQuestion {
    GENERATED_BODY()

protected:
    virtual void NativeOnActivated() override {
        Super::NativeOnActivated();
        // Menu is now visible and focused
        UE_LOG(LogTemp, Warning, TEXT("Menu activated"));
    }

    virtual void NativeOnDeactivated() override {
        Super::NativeOnDeactivated();
        // Menu is now hidden
        UE_LOG(LogTemp, Warning, TEXT("Menu deactivated"));
    }

    virtual UQuestion* NativeGetDesiredFocusTarget() const override {
        // Return question that should receive focus (e.g., first button)
        return PlayButton;
    }

private:
    UPROPERTY(meta = (BindQuestion))
    TObjectPtr<UCommonButtonBase> PlayButton;
};
```

---

### CommonButtonBase (Input-Aware Button)

Replaces standard UMG Button. Automatically handles gamepad/mouse/keyboard input.

```cpp
#include "CommonButtonBase.h"

UCLASS()
class UMyMenuQuestion : public UCommonActivatableQuestion {
    GENERATED_BODY()

protected:
    UPROPERTY(meta = (BindQuestion))
    TObjectPtr<UCommonButtonBase> PlayButton;

    virtual void NativeConstruct() override {
        Super::NativeConstruct();

        // Bind button click (works with any input method)
        PlayButton->OnClicked().AddUObject(this, &UMyMenuQuestion::OnPlayClicked);

        // Set button text
        PlayButton->SetButtonText(FText::FromString(TEXT("Play")));
    }

    void OnPlayClicked() {
        UE_LOG(LogTemp, Warning, TEXT("Play clicked"));
    }
};
```

---

### CommonTextBlock (Styled Text)

Text question with CommonUI styling support.

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UCommonTextBlock> TitleText;

TitleText->SetText(FText::FromString(TEXT("Main Menu")));
```

---

### CommonActionQuestion (Input Prompts)

Displays input prompts (e.g., "Press A to Continue", automatically shows correct button icon).

```cpp
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UCommonActionQuestion> ConfirmActionQuestion;

// Bind to input action
ConfirmActionQuestion->SetInputAction(ConfirmInputActionData);
// Automatically shows correct icon (A on Xbox, X on PlayStation, Enter on PC)
```

---

## Question Stack (Screen Management)

### CommonActivatableQuestionStack

Manages a stack of screens (e.g., Main Menu → Settings → Controls).

```cpp
#include "Questions/CommonActivatableQuestionContainer.h"

UPROPERTY(meta = (BindQuestion))
TObjectPtr<UCommonActivatableQuestionStack> QuestionStack;

// Push new screen onto stack
void ShowSettingsMenu() {
    QuestionStack->AddQuestion(USettingsMenuQuestion::StaticClass());
}

// Pop current screen (go back)
void GoBack() {
    QuestionStack->DeactivateQuestion();
}
```

---

## Input Actions (CommonUI Style)

### Define Input Actions

Create **Common Input Action Data Table**:
1. Content Browser > Miscellaneous > Data Table
2. Row Structure: `CommonInputActionDataBase`
3. Add rows for actions (Confirm, Cancel, Navigate, etc.)

Example row:
- **Action Name**: Confirm
- **Default Input**: Gamepad Face Button Bottom (A/Cross)
- **Alternate Inputs**: Enter (keyboard), Left Mouse Button

---

### Bind Input Actions in Question

```cpp
#include "Input/CommonUIActionRouterBase.h"

UCLASS()
class UMyQuestion : public UCommonActivatableQuestion {
    GENERATED_BODY()

protected:
    virtual void NativeOnActivated() override {
        Super::NativeOnActivated();

        // Bind input action
        FBindUIActionArgs BindArgs(ConfirmInputAction, FSimpleDelegate::CreateUObject(this, &UMyQuestion::OnConfirm));
        BindArgs.bDisplayInActionBar = true; // Show in action bar
        RegisterUIActionBinding(BindArgs);
    }

    void OnConfirm() {
        UE_LOG(LogTemp, Warning, TEXT("Confirmed"));
    }

private:
    UPROPERTY(EditDefaultsOnly, Category = "Input")
    FDataTableRowHandle ConfirmInputAction;
};
```

---

## Focus & Navigation

### Automatic Gamepad Navigation

CommonUI automatically handles gamepad navigation (D-Pad/Stick to move between buttons).

```cpp
// In Question Blueprint:
// - Questions are automatically navigable if they inherit from CommonButton/CommonUserQuestion
// - Focus order is determined by question hierarchy and layout
```

### Custom Focus Navigation

```cpp
// Override focus navigation
virtual UQuestion* NativeGetDesiredFocusTarget() const override {
    return FirstButton; // Return question that should receive focus
}
```

---

## Input Mode (Game vs UI)

### Switch Input Mode

```cpp
#include "CommonUIExtensions.h"

// Switch to UI-only mode (pause game, show cursor)
UCommonUIExtensions::PushStreamedGameplayUIInputConfig(this, FrontendInputConfig);

// Return to game mode (hide cursor, resume gameplay)
UCommonUIExtensions::PopInputConfig(this);
```

---

## Platform-Specific Input Icons

### Configure Input Icons

1. Create **Common Input Base Controller Data** asset for each platform:
   - Gamepad (Xbox, PlayStation, Switch)
   - Mouse & Keyboard
   - Touch

2. Assign platform-specific icons:
   - Gamepad Face Button Bottom: `A` (Xbox), `Cross` (PlayStation)
   - Confirm Key: `Enter` icon

3. Assign to **Common Input Settings** asset

### Automatically Display Correct Icons

```cpp
// CommonActionQuestion automatically shows correct icon for current platform
UPROPERTY(meta = (BindQuestion))
TObjectPtr<UCommonActionQuestion> JumpActionQuestion;

JumpActionQuestion->SetInputAction(JumpInputActionData);
// Shows "A" on Xbox, "Cross" on PlayStation, "Space" on PC
```

---

## Common Patterns

### Main Menu with Navigation

```cpp
UCLASS()
class UMainMenuQuestion : public UCommonActivatableQuestion {
    GENERATED_BODY()

protected:
    UPROPERTY(meta = (BindQuestion))
    TObjectPtr<UCommonButtonBase> PlayButton;

    UPROPERTY(meta = (BindQuestion))
    TObjectPtr<UCommonButtonBase> SettingsButton;

    UPROPERTY(meta = (BindQuestion))
    TObjectPtr<UCommonButtonBase> QuitButton;

    virtual void NativeConstruct() override {
        Super::NativeConstruct();

        PlayButton->OnClicked().AddUObject(this, &UMainMenuQuestion::OnPlayClicked);
        SettingsButton->OnClicked().AddUObject(this, &UMainMenuQuestion::OnSettingsClicked);
        QuitButton->OnClicked().AddUObject(this, &UMainMenuQuestion::OnQuitClicked);
    }

    virtual UQuestion* NativeGetDesiredFocusTarget() const override {
        return PlayButton; // Focus "Play" button when menu opens
    }

    void OnPlayClicked() { /* Start game */ }
    void OnSettingsClicked() { /* Open settings */ }
    void OnQuitClicked() { /* Quit game */ }
};
```

---

### Pause Menu with Back Action

```cpp
UCLASS()
class UPauseMenuQuestion : public UCommonActivatableQuestion {
    GENERATED_BODY()

protected:
    UPROPERTY(EditDefaultsOnly, Category = "Input")
    FDataTableRowHandle BackInputAction; // Assign "Cancel" action in Blueprint

    virtual void NativeOnActivated() override {
        Super::NativeOnActivated();

        // Bind "Back" input (B/Circle/Escape)
        FBindUIActionArgs BindArgs(BackInputAction, FSimpleDelegate::CreateUObject(this, &UPauseMenuQuestion::OnBack));
        RegisterUIActionBinding(BindArgs);
    }

    void OnBack() {
        DeactivateQuestion(); // Close pause menu
    }
};
```

---

## Performance Tips

- Use **CommonActivatableQuestionStack** for screen management (automatically handles activation/deactivation)
- Avoid creating/destroying questions every frame (reuse questions)
- Use **Lazy Questions** for complex menus (only create when needed)

---

## Debugging

### CommonUI Debug Commands

```cpp
// Console commands:
// CommonUI.DumpActivatableTree - Show active question hierarchy
// CommonUI.DumpActionBindings - Show registered input actions
```

---

## Sources
- https://docs.unrealengine.com/5.7/en-US/commonui-plugin-for-advanced-user-interfaces-in-unreal-engine/
- https://docs.unrealengine.com/5.7/en-US/commonui-quickstart-guide-for-unreal-engine/
