// The 17 judge-supported languages (mirrors the judge's actual RUNNERS dict,
// see apps/backend/algorithm_atlas/api/v1/notebook.py, and
// apps/backend/algorithm_atlas/api/v1/problems.py's TARGET_LANGUAGES_TOTAL).
// Shared by ProblemPage's language picker and the catalog's language-coverage
// badges so the denominator/labels never drift apart.
export interface LanguageInfo {
  value: string;
  label: string;
  devicon: string;
}

export const ALL_LANGUAGES: LanguageInfo[] = [
  { value: 'python',     label: 'Python',     devicon: 'devicon-python-plain colored' },
  { value: 'javascript', label: 'JavaScript', devicon: 'devicon-javascript-plain colored' },
  { value: 'typescript', label: 'TypeScript', devicon: 'devicon-typescript-plain colored' },
  { value: 'cpp',        label: 'C++',        devicon: 'devicon-cplusplus-plain colored' },
  { value: 'c',          label: 'C',          devicon: 'devicon-c-plain colored' },
  { value: 'java',       label: 'Java',       devicon: 'devicon-java-plain colored' },
  { value: 'go',         label: 'Go',         devicon: 'devicon-go-plain colored' },
  { value: 'rust',       label: 'Rust',       devicon: 'devicon-rust-plain colored' },
  { value: 'shell',      label: 'Shell',      devicon: 'devicon-bash-plain colored' },
  { value: 'ruby',       label: 'Ruby',       devicon: 'devicon-ruby-plain colored' },
  { value: 'kotlin',     label: 'Kotlin',     devicon: 'devicon-kotlin-plain colored' },
  { value: 'swift',      label: 'Swift',      devicon: 'devicon-swift-plain colored' },
  { value: 'r',          label: 'R',          devicon: 'devicon-r-plain colored' },
  { value: 'csharp',     label: 'C#',         devicon: 'devicon-csharp-plain colored' },
  { value: 'php',        label: 'PHP',        devicon: 'devicon-php-plain colored' },
  { value: 'scala',      label: 'Scala',      devicon: 'devicon-scala-plain colored' },
  { value: 'perl',       label: 'Perl',       devicon: 'devicon-perl-plain colored' },
];

export const TARGET_LANGUAGES_TOTAL = ALL_LANGUAGES.length;

export function languageLabel(value: string): string {
  return ALL_LANGUAGES.find((l) => l.value === value)?.label ?? value;
}
