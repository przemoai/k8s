import {Component} from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {FormsModule} from "@angular/forms";
import {NgForOf} from "@angular/common";

interface Task {
  id: number;
  description: string;
  created_at: string;
}

@Component({
  selector: 'app-todo',
  standalone: true,
  imports: [FormsModule, NgForOf],
  templateUrl: './todo.component.html',
  styleUrl: './todo.component.scss'
})
export class TodoComponent {
  tasks: Task[] = [];
  newTask: string = '';

  constructor(private http: HttpClient) {
    this.loadTasks();
  }

  loadTasks() {
    this.http.get<Task[]>('http://backend-query.deafult.svc.cluster.local/tasks/').subscribe(data => {
      this.tasks = data;
    });
  }

  addTask() {
    if (this.newTask.trim()) {
      this.http.post('http://backend-command.deafult.svc.cluster.local/tasks/', {description: this.newTask}).subscribe(() => {
        this.loadTasks();
        this.newTask = '';
      });
    }
  }

  removeTask(task: Task) {
    this.http.delete('http://backend-command.deafult.svc.cluster.local/tasks/',{body:task}).subscribe(() => {
      this.loadTasks();
    });
  }
}
