import { Component } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {FormsModule} from "@angular/forms";
import {NgForOf} from "@angular/common";

@Component({
  selector: 'app-todo',
  standalone: true,
  imports: [
    FormsModule,
    NgForOf
  ],
  templateUrl: './todo.component.html',
  styleUrl: './todo.component.scss'
})
export class TodoComponent {
  tasks: string[] = [];
  newTask: string = '';

  constructor(private http: HttpClient) {
    this.loadTasks();
  }

  loadTasks() {
    this.http.get<string[]>('http://query-backend/tasks').subscribe(data => {
      this.tasks = data;
    });
  }

  addTask() {
    if (this.newTask.trim()) {
      this.http.post('http://command-backend/add', { task: this.newTask }).subscribe(() => {
        this.loadTasks();
        this.newTask = '';
      });
    }
  }

  removeTask(index: number) {
    const task = this.tasks[index];
    this.http.post('http://command-backend/remove', { task }).subscribe(() => {
      this.loadTasks();
    });
  }
}
