// classDiagram
//     class User {
//         +String name
//         +int time_available
//         +dict preferences
//     }

//     class Pet {
//         +String name
//         +String species
//         +User owner
//     }

//     class Task {
//         +String name
//         +String category
//         +int duration
//         +String priority
//         +Pet pet
//         +String notes
//     }

//     class ScheduledTask {
//         +Task task
//         +int order
//         +String status
//     }

//     class DailyPlan {
//         +String date
//         +User user
//         +Pet pet
//         +List~ScheduledTask~ scheduled_tasks
//         +List~Task~ skipped_tasks
//         +int time_available
//         +int time_used
//         +String reasoning
//     }

//     User "1" --> "1" Pet : owns
//     Pet "1" --> "0..*" Task : has
//     DailyPlan "1" --> "1" User : belongs to
//     DailyPlan "1" --> "1" Pet : for
//     DailyPlan "1" --> "0..*" ScheduledTask : contains
//     DailyPlan "1" --> "0..*" Task : skipped
//     ScheduledTask "1" --> "1" Task : wraps
