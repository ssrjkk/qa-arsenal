import { v4 as uuidv4 } from 'uuid';

const FIRST_NAMES = [
  'Alex',
  'Jordan',
  'Taylor',
  'Morgan',
  'Casey',
  'Riley',
  'Quinn',
  'Avery',
  'Blake',
  'Drew',
];
const LAST_NAMES = [
  'Smith',
  'Johnson',
  'Williams',
  'Brown',
  'Jones',
  'Garcia',
  'Miller',
  'Davis',
  'Martinez',
  'Wilson',
];
const DOMAINS = ['test.com', 'example.com', 'demo.com', 'mail.com', 'testmail.com'];

export interface IUserData {
  email: string;
  name: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface ITodoData {
  title: string;
  completed: boolean;
}

const generateRandomString = (length: number): string => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

const generateId = (): string => {
  return uuidv4();
};

export const DataFactory = {
  generateUniqueId: (): string => {
    return generateId();
  },

  generateRandomString,

  generateEmail: (prefix?: string): string => {
    const id = generateId().slice(0, 8);
    const domain = DOMAINS[Math.floor(Math.random() * DOMAINS.length)];
    const emailPrefix = prefix || `user${id}`;
    return `${emailPrefix}_${Date.now()}@${domain}`;
  },

  generateName: (): string => {
    const firstName = FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)];
    const lastName = LAST_NAMES[Math.floor(Math.random() * LAST_NAMES.length)];
    return `${firstName} ${lastName}`;
  },

  generateFirstName: (): string => {
    return FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)];
  },

  generateLastName: (): string => {
    return LAST_NAMES[Math.floor(Math.random() * LAST_NAMES.length)];
  },

  generatePassword: (length: number = 12): string => {
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';
    const special = '!@#$%^&*';
    const allChars = uppercase + lowercase + numbers + special;

    let password = '';
    password += uppercase[Math.floor(Math.random() * uppercase.length)];
    password += lowercase[Math.floor(Math.random() * lowercase.length)];
    password += numbers[Math.floor(Math.random() * numbers.length)];
    password += special[Math.floor(Math.random() * special.length)];

    for (let i = 4; i < length; i++) {
      password += allChars[Math.floor(Math.random() * allChars.length)];
    }

    return password
      .split('')
      .sort(() => Math.random() - 0.5)
      .join('');
  },

  generateUser: (overrides?: Partial<IUserData>): IUserData => {
    const firstName = DataFactory.generateFirstName();
    const lastName = DataFactory.generateLastName();

    return {
      email: DataFactory.generateEmail(),
      name: `${firstName} ${lastName}`,
      password: DataFactory.generatePassword(),
      firstName,
      lastName,
      ...overrides,
    };
  },

  generateTodo: (overrides?: Partial<ITodoData>): ITodoData => {
    const titles = [
      'Buy groceries',
      'Finish report',
      'Call dentist',
      'Book flight',
      'Send email',
      'Review PR',
      'Update documentation',
      'Fix bug',
      'Write tests',
      'Deploy to staging',
    ];

    return {
      title:
        titles[Math.floor(Math.random() * titles.length)] +
        ` ${DataFactory.generateUniqueId().slice(0, 4)}`,
      completed: false,
      ...overrides,
    };
  },

  generateMultipleUsers: (count: number): IUserData[] => {
    return Array.from({ length: count }, () => DataFactory.generateUser());
  },

  generateMultipleTodos: (count: number): ITodoData[] => {
    return Array.from({ length: count }, () => DataFactory.generateTodo());
  },

  generateInvalidEmail: (): string => {
    const invalidPatterns = [
      'notanemail',
      'missing@domain',
      '@nodomain.com',
      'spaces in@email.com',
      'test@.com',
      'test@domain',
    ];
    return invalidPatterns[Math.floor(Math.random() * invalidPatterns.length)];
  },

  generateWeakPassword: (): string => {
    const weakPasswords = ['password', '123456', 'qwerty', 'admin', 'letmein', 'abc123'];
    return weakPasswords[Math.floor(Math.random() * weakPasswords.length)];
  },

  generateLongText: (length: number): string => {
    return 'a'.repeat(length);
  },

  generateSearchQuery: (): string => {
    const queries = ['test', 'sample', 'demo', 'example', 'check', 'find', 'search', 'query'];
    return queries[Math.floor(Math.random() * queries.length)] + ' ' + generateId().slice(0, 4);
  },
};
