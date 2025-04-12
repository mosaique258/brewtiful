---
title: api specification
date: 2025-01-03
categories:
  - Technical 
tags:
  - API
  - Specification
  - NamingConvention
  - Security
  - ErrorHandling
  - Versioning
  - DataValidation
---

# API Specification: Brewtiful Ecosystem

## 1. Introduction

This document details the low-level API design for the Brewtiful ecosystem, focusing on the interactions between the Smart Coffee Machine and its connected systems. It builds upon the high-level design document, providing detailed specifications for each API call, including parameters, return values, error handling, and security considerations. This document is intended for developers working on the Coffee Machine firmware, ESB configuration, and integration with the various enterprise systems.

## 2. System Architecture

The system comprises the following key components:

*   **Smart Coffee Machine (Core System):** Brews coffee tailored to user mood and preferences.
*   **Enterprise Service Bus (ESB):** Acts as a central communication hub, routing requests and data between the coffee machine and other enterprise systems (CRM, ERP, analysis services, recipe management).
*   **Customer Relationship Management (CRM) System:** Stores and manages customer profiles, purchase history, and preferences.
*   **Enterprise Resource Planning (ERP) System:** Manages inventory, supply chain, and procurement.
*   **Voice Analysis System:** Analyzes the user's voice for emotional tone.
*   **Facial Recognition and Emotion Detection System:** Identifies facial expressions and maps them to emotional states.
*   **Coffee Recipe Management System:** Maps emotional states to specific coffee recipes.

Also have a look at the [[high_level_design]]. 

## 3. Naming Conventions

*   **CM_**:  API calls originating from the Smart Coffee Machine (internal control).
*   **ESB_**: API calls originating from (and *exposed by*) the Enterprise Service Bus.
*   **CRM_**: API calls internal to the CRM system (accessed only via the ESB).
*   **ERP_**: API calls internal to the ERP system (accessed only via the ESB).

All dates will be in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ).  Currency will be represented as a string using ISO 4217 currency codes (e.g., "USD 12.50").

## 4. Security

*   **API Keys:** All API calls *exposed by the ESB* require an API Key passed in the `X-API-Key` header.  The ESB is responsible for managing and provisioning API Keys.
*   **Internal Authentication:**  Internal Coffee Machine APIs (`CM_BrewCoffee`, `CM_DispenseCoffee`, `CM_GetMachineStatus`) use a separate authentication mechanism (e.g., JWT - JSON Web Token) managed by the microcontroller's security module.  This is *not* exposed externally.
*   **TLS:** TLS 1.3 or higher is *required* for all communication between components.
*   **OAuth 2.0:** The ESB uses OAuth 2.0 to securely access the CRM and ERP systems.  This provides delegated authorization.
*   **Input Validation:**  *Mandatory* input validation on all API endpoints to prevent injection attacks (SQL injection, command injection, etc.).

## 5. Error Handling

All API calls (except internal coffee machine calls) return a standard error format in case of failure:

```json
{
  "errorCode": "ERROR_CODE",
  "errorMessage": "Detailed error message",
  "timestamp": "YYYY-MM-DDTHH:mm:ssZ",
  "details": {  }
}
```

*   **`errorCode`**:  A unique string identifier for the error.
*   **`errorMessage`**: A human-readable description of the error.
*   **`timestamp`**:  The time the error occurred (ISO 8601 format).
*   **`details`**:  An optional object containing additional error-specific details (e.g., validation errors, stack traces in development environments).

Error codes are specific to each API and documented below.

## 6. Versioning

APIs are versioned using a suffix in the API name (e.g., `ESB_GetCustomerProfile_v1`). This allows for backward-compatible changes and the deprecation of older versions.  The absence of a version suffix implies version 1.

## 7. Data Validation

All input parameters *must* be validated against predefined schemas. Invalid data *must* result in a `400 Bad Request` HTTP error, with a detailed error message in the standard error format (see section 5) indicating the specific validation failures.

## 8. API Definitions

### 8.1 Smart Coffee Machine (CM_) APIs

The Smart Coffee Machine interacts *exclusively* with the ESB.  The `CM_` APIs listed here are *internal* to the coffee machine (device control).

*   **`CM_BrewCoffee_v1` (Internal):**
    *   **Purpose:** Initiates the coffee brewing process.  *This is an internal control API, not exposed externally.*
    *   **Parameters:**
        *   `recipeID` (string, required): The ID of the recipe to brew (obtained from `ESB_GetRecipe_v1`).
        *   `ingredientQuantities` (JSON, required):  The actual quantities of each ingredient to use, potentially adjusted based on `ESB_CheckInventoryLevel_v1` results.  Example: `{"ingredientID1": 25.0, "ingredientID2": 150.0}`
    *   **Return Value:**
        ```json
        {
          "status": "Brewing" | "Completed" | "Error" | "InsufficientSkills"
        }
        ```
        *   `InsufficientSkills` indicates a maintenance issue (e.g., descaling needed).
    *   **Description:**  Controls the physical brewing hardware (grinder, water pump, heater, etc.).  This API is *not* exposed externally and uses internal authentication.
    *   **Error Codes:** (Internal to the Coffee Machine, not in standard error format)
        *   `CM_BREW_FAILED`: A general brewing error (e.g., mechanical failure).
        *   `CM_INSUFFICIENT_INGREDIENTS`:  Not enough of a required ingredient.
        *   `CM_INVALID_RECIPE_ID`: The provided `recipeID` is not valid.
    *   **Security:** Internal authentication (e.g., JWT).

*   **`CM_DispenseCoffee_v1` (Internal):**
    *   **Purpose:** Dispenses the brewed coffee. *Internal control API.*
    *   **Parameters:**
        *   `quantity` (float, required): The amount of coffee to dispense (in ml).
        *   `temperature` (float, required): The desired temperature of the dispensed coffee (in Celsius).
    *   **Return Value:**
        ```json
        {
          "status": "Dispensing" | "Completed" | "Error"
        }
        ```
    *   **Description:** Controls the dispensing mechanism. This API is *not* exposed externally.
    *   **Error Codes:** (Internal)
        *   `CM_DISPENSE_FAILED`:  A general dispensing error.
        *   `CM_INVALID_QUANTITY`: The `quantity` is invalid (e.g., negative or exceeds limits).
        *   `CM_INVALID_TEMPERATURE`: The `temperature` is invalid.
    *   **Security:** Internal authentication (e.g., JWT).

*   **`CM_GetMachineStatus_v1` (Internal):**
    *   **Purpose:**  Retrieves the current operational status of the coffee machine. *Internal control API.*
    *   **Parameters:** None
    *   **Return Value:**
        ```json
        {
          "temperature": (float, Celsius),
          "waterLevel": (integer, ml),
          "beanLevel": (integer, grams),
          "isGrinderEmpty": (boolean),
          "isCupPresent": (boolean),
          "lastMaintenance": (string, ISO 8601 format)
        }
        ```
    *   **Description:** Provides real-time status information.  This API is *not* exposed externally.
    *   **Error Codes:** None (returns default values if status retrieval fails).
    *   **Security:** Internal authentication (e.g., JWT).

### 8.2 ESB (ESB_) APIs

These APIs are *exposed by* the ESB and are the *only* way the Smart Coffee Machine interacts with external systems.

*   **`ESB_GetCustomerProfile_v1`:**
    *   **Purpose:** Retrieves customer profile information from the CRM.
    *   **Parameters:**
        *   `customerID` (string, optional):  The customer's ID.  If not provided, a default "guest" profile is returned.
    *   **Return Value:**
        ```json
        {
          "customerID": (string),
          "name": (string),
          "preferences": {
            "coffeeType": (string, "Espresso" | "Latte" | "Cappuccino" | ...),
            "milkType": (string, "Whole" | "Skim" | "Almond" | "Soy" | "Oat" | "None"),
            "sugarLevel": (integer, 0-5), // 0 = none, 5 = very sweet
            "temperaturePreference": (float, Celsius) // Preferred serving temperature
          },
          "loyaltyPoints": (integer),
          "email": (string, email format), // Optional, may be null
          "optInPromotions": (boolean)
        }
        ```
        Returns a 404 HTTP status code if the customer is not found.
    *   **Description:** The ESB retrieves the customer profile from the CRM (using `CRM_GetCustomerProfile_v1`).
    *   **Error Codes:**
        *   `ESB_CRM_UNAVAILABLE`: The CRM system is unavailable.
        *   `ESB_TRANSFORMATION_ERROR`: Data transformation failed (e.g., mapping CRM data to the expected format).
        *   `ESB_INVALID_CUSTOMER_ID`: The provided customer ID is invalid.
    *   **Security:** Requires API Key in `X-API-Key` header.

*   **`ESB_CheckInventoryLevel_v1`:**
    *   **Purpose:** Checks the inventory level of one or more ingredients in the ERP system.
    *   **Parameters:**
        *   `ingredients` (array of strings, required): An array of ingredient IDs to check.
    *   **Return Value:**
        ```json
        {
          "ingredientStatuses": [
            { "ingredientID": (string), "isAvailable": (boolean), "quantityAvailable": (float, units), "unit": (string)}
          ]
        }
        ```
    *   **Description:**  The ESB queries the ERP (using `ERP_CheckInventoryLevel_v1`) for ingredient availability.
    *   **Error Codes:**
        *   `ESB_ERP_UNAVAILABLE`: The ERP system is unavailable.
        *   `ESB_TRANSFORMATION_ERROR`: Data transformation failed.
        *   `ESB_INVALID_INGREDIENT_ID`: An invalid ingredient ID was provided.
    *   **Security:** Requires API Key in `X-API-Key` header.

*   **`ESB_UpdateInventoryLevel_v1`:**
    *    **Purpose:** Updates inventory levels in the ERP after coffee is brewed.
    *    **Parameters:**
    *       `ingredientID` (string, required): Ingredient ID.
    *       `quantity` (float, required): The amount to adjust the inventory by (negative for consumption or positive for restock).
    *     `unit` (string, required): The unit of measurement.
    *   **Return Value:** A JSON object with a `status` of "Success" or "Failed".
        ```json
        {
          "status": "Success" | "Failed"
        }
        ```
    *   **Description:**  The ESB sends the inventory update to the ERP (using ERP_UpdateInventoryLevel).
    *   **Error Codes:**
    *     `ESB_ERP_UNAVAILABLE`: The ERP system is unavailable.
        *   `ESB_TRANSFORMATION_ERROR`: Data transformation failed.
    *   **Security:** Requires API Key in `X-API-Key` header.

*   **`ESB_AnalyzeFace_v1`:**
    *   **Purpose:**  Analyzes the user's facial image to determine mood.
    *   **Parameters:**
        *   `imageData` (byte array, required): The user's facial image data (JPEG format), Base64 encoded.
    *   **Return Value:**
        ```json
        {
          "moodVector": {
            "happiness": (float, 0.0-1.0),
            "sadness": (float, 0.0-1.0),
            "tiredness": (float, 0.0-1.0),
            "anger": (float, 0.0-1.0),
            "neutral": (float, 0.0-1.0)
          },
          "moodConfidence": (float, 0.0-1.0)
        }
        ```
    *   **Description:** The ESB forwards the image data to the Facial Recognition and Emotion Detection System.
    *   **Error Codes:**
        *   `ESB_FACE_SYS_UNAVAILABLE`:  The facial analysis system is unavailable.
        *   `ESB_TRANSFORMATION_ERROR`:  Data transformation failed.
        *   `ESB_INVALID_IMAGE_FORMAT`: The image data is not in the correct format (JPEG).
    *   **Security:** Requires API Key in `X-API-Key` header.

*   **`ESB_AnalyzeVoice_v1`:**
    *   **Purpose:** Analyzes the user's voice data to determine mood.
    *   **Parameters:**
        *   `audioData` (byte array, required): The user's voice audio data (PCM, 16-bit, 44.1kHz), Base64 encoded.
    *   **Return Value:** (Same `moodVector` format as `ESB_AnalyzeFace_v1`)
        ```json
        {
          "moodVector": {
            "happiness": (float, 0.0-1.0),
            "sadness": (float, 0.0-1.0),
            "tiredness": (float, 0.0-1.0),
            "anger": (float, 0.0-1.0),
            "neutral": (float, 0.0-1.0)
          },
          "moodConfidence": (float, 0.0-1.0)
        }
        ```
    *   **Description:** The ESB forwards the audio data to the Voice Analysis System.
    *   **Error Codes:**
        *   `ESB_VOICE_SYS_UNAVAILABLE`: The voice analysis system is unavailable.
        *   `ESB_TRANSFORMATION_ERROR`: Data transformation failed.
        *   `ESB_INVALID_AUDIO_FORMAT`: The audio data is not in the correct format (PCM, 16-bit, 44.1kHz).
    *   **Security:** Requires API Key in `X-API-Key` header.

*   **`ESB_GetRecipe_v1`:**
    *   **Purpose:** Selects the optimal coffee recipe based on mood and customer preferences.
    *   **Parameters:**
        *   `moodVector` (object, required): The user's mood vector (from `ESB_AnalyzeFace_v1` and/or `ESB_AnalyzeVoice_v1`).
        *   `customerPreferences` (object, required): The customer's preferences (from `ESB_GetCustomerProfile_v1`).
    *   **Return Value:**
        ```json
        {
          "recipeID": (string),
          "recipeName": (string),
          "ingredients": [
            { "ingredientID": (string), "name": (string), "quantity": (float), "unit": (string) }
          ],
          "brewingInstructions": (string),
          "requiredSkills": [
            { "skillID": (string), "skillName": (string)}
          ]

        }
        ```
    *   **Description:**  The ESB queries the Coffee Recipe Management System to find the best matching recipe.
    *   **Error Codes:**
        *   `ESB_RECIPE_SYS_UNAVAILABLE`: The recipe management system is unavailable.
        *   `ESB_TRANSFORMATION_ERROR`:  Data transformation failed.
        *   `ESB_NO_MATCHING_RECIPE`: No suitable recipe was found for the given mood and preferences.
    *   **Security:** Requires API Key in `X-API-Key` header.

*   **`ESB_ApplyLoyaltyDiscount_v1`:**
    *   **Purpose:** Apply a loyalty discount to an order.  This is called *before* brewing, to calculate the price.
    *   **Parameters:**
        *   `customerID` (string, required):  The customer's ID.
        *   `orderTotal` (string, required): The initial order total (currency, e.g., "USD 4.50").
    *   **Return Value:**
        ```json
        {
          "discountedTotal": (string), // e.g., "USD 4.00"
          "pointsRemaining": (integer),
          "status": "Success" | "Failed" | "InsufficientPoints"
        }
        ```
    *   **Description:** The ESB interacts with the CRM (using `CRM_ApplyLoyaltyDiscount_v1`) to apply any applicable discounts.
    *   **Error Codes:**
        *   `ESB_CRM_UNAVAILABLE`: The CRM system is unavailable.
        *   `ESB_TRANSFORMATION_ERROR`: Data transformation failed.
        *   `ESB_INVALID_INPUT`: Invalid input data.
    *   **Security:** Requires API Key in `X-API-Key` header.


### 8.3 CRM (CRM_) APIs (Internal - Accessed via ESB)

These APIs are *internal* to the CRM system and are *only* accessed via the ESB.

*   **`CRM_GetCustomerProfile_v1`:**
    *   **Purpose:** Retrieves a customer profile based on their ID.
    *   **Parameters:**
        *    `customerID` (string, required): Customer ID.
    *   **Return Value**:
        ```json
        {
          "customerID": (string),
          "name": (string),
          "preferences": {
            "coffeeType": (string, "Espresso" | "Latte" | "Cappuccino" | ...),
            "milkType": (string, "Whole" | "Skim" | "Almond" | "Soy" | "Oat" | "None"),
            "sugarLevel": (integer, 0-5), // 0 = none, 5 = very sweet
            "temperaturePreference": (float, Celsius) // Preferred serving temperature
            },
          "loyaltyPoints": (integer),
          "email": (string, email format), // Optional, may be null
          "optInPromotions": (boolean)
        }
        ```
    *   **Description:** Retrieves customer data from the CRM database.
    *   **Error Codes:**
        *   `CRM_CUSTOMER_NOT_FOUND`: Customer not found.
        *   `CRM_DATABASE_ERROR`: Error accessing the CRM database.
    *    **Security:** OAuth 2.0 (accessed by the ESB).

*   **`CRM_UpdateCustomerPreferences_v1`:**
    *   **Purpose:** Updates a customer's preferences.
    *   **Parameters:**
        *    `customerID` (string, required): Customer ID.
        *    `preferences` (JSON, required): Customer preferences (same format as in `CRM_GetCustomerProfile_v1`).
    *   **Return Value:**
        ```json
        { "status": (string, "Success", "Failed") }
        ```
    *   **Description:** Updates customer preferences in the CRM database.
    *   **Error Codes:**
        *    `CRM_CUSTOMER_NOT_FOUND`: Customer not found.
        *    `CRM_DATABASE_ERROR`: Error accessing the CRM database.
        *   `CRM_INVALID_PREFERENCES`: Invalid preferences format.
    *   **Security:** OAuth 2.0 (accessed by the ESB).

*   **`CRM_CreateCustomerProfile_v1`:**
    *   **Purpose:** Creates a new customer profile.
    *   **Parameters:**
        *   `profileData` (JSON, required): Customer profile data. Format should include name, email, and default preferences. It is best to require minimal information on creation.
    *   **Return Value:**
        ```json
        {
          "customerID": (string),  // Newly generated customer ID
          "status": (string, "Success", "Failed")
        }
        ```
    *    **Description:** Creates a new customer profile in the CRM database.
    *    **Error Codes:**
        *   `CRM_DATABASE_ERROR`: Error accessing the CRM database.
        *   `CRM_INVALID_PROFILE_DATA`: Invalid profile data format.
    *   **Security:** OAuth 2.0 (accessed by the ESB).

*   **`CRM_ApplyLoyaltyDiscount_v1`:**
    *   **Purpose:** Apply a loyalty discount to an order
    *   **Parameters:**
        *    `customerID` (string, required): Customer ID.
        *   `orderTotal` (string, currency ISO 4217 format, e.g., "USD 3.50")
    *   **Return Value:**
        ```json
        {
          "discountedTotal": (string, currency ISO 4217 format, e.g., "USD 3.00"),
          "pointsRemaining": (integer),
          "status": (string, "Success", "Failed")
        }
        ```
    *    **Description:** Applies a loyalty discount to an order
    *   **Error Codes:**
        *    `CRM_CUSTOMER_NOT_FOUND`: Customer not found.
        *   `CRM_DATABASE_ERROR`: Error accessing the CRM database.
        *   `CRM_INSUFFICIENT_POINTS`: Customer does not have enough loyalty points
        *    `CRM_INVALID_ORDER_TOTAL`: Invalid order total
    *   **Security:** OAuth 2.0 (accessed by the ESB).

### 8.4 ERP (ERP_) APIs (Internal - Accessed via ESB)

These APIs are *internal* to the ERP system and are *only* accessed via the ESB.

*   **`ERP_CheckInventoryLevel_v1`:**
    *    **Purpose:** Checks the current inventory level of an ingredient.
    *   **Parameters:**
        *   `ingredientID` (string, required): Ingredient ID.
    *   **Return Value:**
        ```json
        {
          "isAvailable": (boolean),
          "quantityAvailable": (float, units),
          "unit": (string)
        }
        ```
    *   **Description:** Retrieves the inventory level from the ERP database.
    *    **Error Codes:**
        *   `ERP_INGREDIENT_NOT_FOUND`: Ingredient not found.
        *   `ERP_DATABASE_ERROR`: Error accessing the ERP database.
    *   **Security:** OAuth 2.0 (accessed by the ESB).

*   **`ERP_CreatePurchaseOrder_v1`:**
    *   **Purpose:** Creates a purchase order for an ingredient.
    *   **Parameters:**
        *   `ingredientID` (string, required): Ingredient ID.
        *    `quantity` (float, required): Quantity to order.
        *   `unit` (string, required): Unit of measurement.
    *   **Return Value:**
        ```json
        {
          "purchaseOrderID": (string),
          "status": (string, "Success", "Failed")
        }
        ```
    *    **Description:** Creates a purchase order in the ERP system.
    *    **Error Codes:**
        *    `ERP_INGREDIENT_NOT_FOUND`: Ingredient not found.
        *   `ERP_DATABASE_ERROR`: Error accessing the ERP database.
        *   `ERP_INVALID_QUANTITY`: Invalid quantity value.
    *   **Security:** OAuth 2.0 (accessed by the ESB).

*   **`ERP_UpdateInventoryLevel_v1`:**
    *    **Purpose:** Updates the inventory level of an ingredient.
    *   **Parameters:**
        *   `ingredientID` (string, required): Ingredient ID.
        *   `quantity` (float, required): Quantity to add or subtract (negative for consumption).
        *    `unit` (string, required): Unit of measurement.
    *   **Return Value:**
        ```json
        {
          "status": (string, "Success", "Failed")
        }
        ```
    *   **Description:** Updates the inventory level in the ERP database.
    *   **Error Codes:**
        *   `ERP_INGREDIENT_NOT_FOUND`: Ingredient not found.
        *    `ERP_DATABASE_ERROR`: Error accessing the ERP database.
        *    `ERP_INVALID_QUANTITY`: Invalid quantity value.
    *   **Security:** OAuth 2.0 (accessed by the ESB).


**Tags**  #API #Specification #NamingConvention #Security #ErrorHandling #Versioning #DataValidation 