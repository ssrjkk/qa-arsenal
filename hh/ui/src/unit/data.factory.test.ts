import { describe, expect, it } from 'vitest';
import { DataFactory } from '../data/data.factory';

describe('DataFactory.generateUser', () => {
  it('produces a complete user', () => {
    const user = DataFactory.generateUser();
    expect(user.email).toContain('@');
    expect(user.name).toContain(' ');
    expect(user.firstName.length).toBeGreaterThan(0);
    expect(user.lastName.length).toBeGreaterThan(0);
    expect(user.password.length).toBeGreaterThanOrEqual(12);
  });

  it('applies overrides', () => {
    const user = DataFactory.generateUser({ name: 'Fixed Name' });
    expect(user.name).toBe('Fixed Name');
  });

  it('produces unique emails', () => {
    const a = DataFactory.generateUser();
    const b = DataFactory.generateUser();
    expect(a.email).not.toBe(b.email);
  });
});

describe('DataFactory.generateTodo', () => {
  it('produces a todo with a title and completed flag', () => {
    const todo = DataFactory.generateTodo();
    expect(todo.title.length).toBeGreaterThan(0);
    expect(typeof todo.completed).toBe('boolean');
  });

  it('applies overrides', () => {
    const todo = DataFactory.generateTodo({ completed: true });
    expect(todo.completed).toBe(true);
  });
});

describe('DataFactory helpers', () => {
  it('generateEmail contains an @ and a dot', () => {
    expect(DataFactory.generateEmail()).toMatch(/@.+\./);
  });

  it('generatePassword respects length', () => {
    expect(DataFactory.generatePassword(20).length).toBe(20);
  });

  it('generateFirstName returns a non-empty name', () => {
    expect(DataFactory.generateFirstName().length).toBeGreaterThan(0);
  });

  it('generateLastName returns a non-empty name', () => {
    expect(DataFactory.generateLastName().length).toBeGreaterThan(0);
  });

  it('generateRandomString produces requested length', () => {
    expect(DataFactory.generateRandomString(7).length).toBe(7);
  });

  it('generateUniqueId returns a non-empty id', () => {
    expect(DataFactory.generateUniqueId().length).toBeGreaterThan(0);
  });
});