// MongoDB Script: Camper Travel Checklists
// 
// INSTRUCTIONS:
// 1. Replace PROJECT_ID and USER_ID with your actual values
// 2. Run this script using: mongosh <your-db-connection-string> camper_checklists.js
//    Or copy the content into MongoDB Compass shell
//
// To find your project_id and user_id:
// - Login to your app and go to the project where you want these checklists
// - Check the URL: /projects/<project_id>/checklists
// - Or query: db.projects.find({name: "Your Project Name"}, {id: 1, user_id: 1})

const PROJECT_ID = "REPLACE_WITH_YOUR_PROJECT_ID";  // e.g., "5cea0f68-77e6-462b-8cc6-2128f0f300e1"
const USER_ID = "REPLACE_WITH_YOUR_USER_ID";        // e.g., "admin-user-id"

const now = new Date().toISOString();

// Generate UUID-like IDs
function generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Checklist data from the PDF
const checklists = [
    {
        name: "1. Pre-Trip Planning",
        description: "Essential checks and preparations before starting your camper trip",
        items: [
            "Passport / ID",
            "Driver's license",
            "Vehicle registration",
            "Insurance documents",
            "Breakdown assistance membership",
            "Campsite reservations",
            "Check weather forecast",
            "Check tire pressure (incl. spare)",
            "Check oil, coolant, brake fluid",
            "Gas bottle filled",
            "Waste water tank empty",
            "Toilet cassette empty",
            "Leisure battery charged"
        ]
    },
    {
        name: "2. Packing Essentials",
        description: "Must-have items to pack for your camper trip",
        items: [
            "Bedding & towels",
            "Clothing (weather appropriate)",
            "Toiletries",
            "Cooking utensils",
            "Plates & cutlery",
            "Food & drinks",
            "CEE power cable & adapter",
            "Water hose (food safe)",
            "Leveling blocks",
            "First aid kit",
            "Warning triangle",
            "Fire extinguisher"
        ]
    },
    {
        name: "3. Departure Day",
        description: "Final checks before driving off",
        items: [
            "Windows & roof hatches closed",
            "Steps retracted",
            "Cables disconnected",
            "Loose items secured",
            "Fridge locked",
            "Cabinets locked",
            "Gas turned off",
            "Water pump off",
            "Mirrors adjusted",
            "Navigation set"
        ]
    },
    {
        name: "4. Arrival at Campsite",
        description: "Setup tasks when you arrive at your destination",
        items: [
            "Park level",
            "Handbrake applied",
            "Connect electricity",
            "Connect water",
            "Turn on fridge",
            "Switch water pump on",
            "Test taps",
            "Set heating (if needed)"
        ]
    },
    {
        name: "5. Before Leaving Campsite",
        description: "Checklist before departing from the campsite",
        items: [
            "Disconnect electricity",
            "Drain waste water",
            "Empty toilet cassette",
            "Close roof hatches",
            "Retract steps",
            "Secure loose items",
            "Check surroundings"
        ]
    },
    {
        name: "6. Return / Storage",
        description: "End-of-trip tasks and long-term storage preparation",
        items: [
            "Empty fresh water tank",
            "Empty waste water tank",
            "Clean fridge (leave door open)",
            "Remove food",
            "Turn off gas",
            "Disconnect batteries (long-term storage)",
            "Drain water system (winter)",
            "Open all taps (winter)"
        ]
    }
];

// Insert checklists and items
print("Starting import of Camper Travel Checklists...\n");

checklists.forEach((checklist, index) => {
    const checklistId = generateId();
    
    // Insert the checklist
    const checklistDoc = {
        id: checklistId,
        project_id: PROJECT_ID,
        user_id: USER_ID,
        name: checklist.name,
        description: checklist.description,
        created_at: now,
        updated_at: now
    };
    
    db.checklists.insertOne(checklistDoc);
    print(`✓ Created checklist: ${checklist.name}`);
    
    // Insert all items for this checklist
    checklist.items.forEach((itemText, itemIndex) => {
        const itemDoc = {
            id: generateId(),
            checklist_id: checklistId,
            user_id: USER_ID,
            text: itemText,
            is_done: false,
            order: itemIndex,
            created_at: now,
            updated_at: now
        };
        
        db.checklist_items.insertOne(itemDoc);
    });
    
    print(`  → Added ${checklist.items.length} items\n`);
});

print("========================================");
print("Import complete!");
print(`Total checklists created: ${checklists.length}`);
print(`Total items created: ${checklists.reduce((sum, c) => sum + c.items.length, 0)}`);
print("========================================");
