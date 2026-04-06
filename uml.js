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
//         +String scheduled_time
//         +String due_date
//     }
//
//     class ScheduledTask {
//         +Task task
//         +int order
//         +String status
//         +String scheduled_time
//         +mark_complete(completed_on) Task
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
//         +List~String~ warnings
//         +total_tasks() int
//         +summary() String
//     }
//
//     class Scheduler {
//         +Owner owner
//         +Pet pet
//         +generate(date) DailyPlan
//         +sort_by_time(tasks) List~Task~
//         +check_conflicts(scheduled_tasks) List~String~
//         -_sort_tasks(tasks) List~Task~
//         -_build_reasoning(scheduled, skipped) String
//     }
//
//     class FilterPlans {
//         <<utility>>
//         +filter_plans(plans, pet_name, status) List~ScheduledTask~
//         +detect_conflicts(scheduled_tasks) List~Tuple~
//         -_parse_time(t) int
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
//     Scheduler ..> FilterPlans : delegates conflict detection
//     FilterPlans ..> DailyPlan : reads
//     FilterPlans ..> ScheduledTask : filters
