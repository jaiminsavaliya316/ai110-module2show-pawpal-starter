// classDiagram
//     class Owner {
//         +String name
//         +int time_available
//         +dict preferences
//         +List~Pet~ pets
//     }
//
//     class Pet {
//         +String name
//         +String species
//         +Owner owner
//         +List~Task~ tasks
//         +add_task(task)
//         +remove_task(task)
//     }
//
//     class Task {
//         +String name
//         +String category
//         +int duration
//         +String priority
//         +String frequency
//         +String notes
//     }
//
//     class ScheduledTask {
//         +Task task
//         +int order
//         +String status
//         +mark_complete()
//     }
//
//     class DailyPlan {
//         +String date
//         +Owner owner
//         +Pet pet
//         +int time_available
//         +List~ScheduledTask~ scheduled_tasks
//         +List~Task~ skipped_tasks
//         +int time_used
//         +String reasoning
//         +total_tasks() int
//         +summary() String
//     }
//
//     class Scheduler {
//         +Owner owner
//         +Pet pet
//         +generate(date) DailyPlan
//         -_sort_tasks(tasks) List~Task~
//         -_build_reasoning(scheduled, skipped) String
//     }
//
//     Owner "1" --> "0..*" Pet : owns
//     Pet "1" --> "0..*" Task : has
//     DailyPlan "1" --> "1" Owner : belongs to
//     DailyPlan "1" --> "1" Pet : for
//     DailyPlan "1" --> "0..*" ScheduledTask : contains
//     DailyPlan "1" --> "0..*" Task : skipped
//     ScheduledTask "1" --> "1" Task : wraps
//     Scheduler "1" --> "1" Owner : uses
//     Scheduler "1" --> "1" Pet : schedules
//     Scheduler ..> DailyPlan : creates
