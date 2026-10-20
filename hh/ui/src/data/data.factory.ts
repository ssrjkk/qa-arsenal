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

// Выбор случаётся через crypto, а не Math.random: предсказуемый генератор
// делает «уникальные» почты и пароли повторяемыми между параллельными прогонами,
// и два набора данных начинают сталкиваться одними и теми же аккаунтами.
const randomIndex = (length: number): number => {
  const buffer = new Uint32Array(1);
  crypto.getRandomValues(buffer);
  return buffer[0] % length;
};

const pick = <T>(items: readonly T[]): T => items[randomIndex(items.length)];

const pickChar = (source: string): string => source.charAt(randomIndex(source.length));

const generateRandomString = (length: number): string => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += pickChar(chars);
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
    const domain = pick(DOMAINS);
    const emailPrefix = prefix || `user${id}`;
    return `${emailPrefix}_${Date.now()}@${domain}`;
  },

  generateName: (): string => {
    const firstName = pick(FIRST_NAMES);
    const lastName = pick(LAST_NAMES);
    return `${firstName} ${lastName}`;
  },

  generateFirstName: (): string => {
    return pick(FIRST_NAMES);
  },

  generateLastName: (): string => {
    return pick(LAST_NAMES);
  },

  generatePassword: (length: number = 12): string => {
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';
    const special = '!@#$%^&*';
    const allChars = uppercase + lowercase + numbers + special;

    let password = '';
    password += pickChar(uppercase);
    password += pickChar(lowercase);
    password += pickChar(numbers);
    password += pickChar(special);

    for (let i = 4; i < length; i++) {
      password += pickChar(allChars);
    }

    // Тасование Фишера–Йетса: `sort(() => Math.random() - 0.5)` не равномерное
    // перемешивание и зависит от алгоритма сортировки движка.
    const chars = password.split('');
    for (let i = chars.length - 1; i > 0; i--) {
      const j = randomIndex(i + 1);
      [chars[i], chars[j]] = [chars[j], chars[i]];
    }
    return chars.join('');
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
        pick(titles) +
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
    return pick(invalidPatterns);
  },

  generateWeakPassword: (): string => {
    const weakPasswords = ['password', '123456', 'qwerty', 'admin', 'letmein', 'abc123'];
    return pick(weakPasswords);
  },

  generateLongText: (length: number): string => {
    return 'a'.repeat(length);
  },

  generateSearchQuery: (): string => {
    const queries = ['test', 'sample', 'demo', 'example', 'check', 'find', 'search', 'query'];
    return pick(queries) + ' ' + generateId().slice(0, 4);
  },
};
