export const STATUS_MAP: Record<string, string> = {
  available: 'Disponível',
  reserved: 'Reservado',
  occupied: 'Ocupado',
  blocked: 'Bloqueado',
  maintenance: 'Manutenção',
};

export const PRIORITY_MAP: Record<string, string> = {
  low: 'Baixa',
  medium: 'Média',
  high: 'Alta',
  emergency: 'Emergência',
};

export const ROLE_MAP: Record<string, string> = {
  admin: 'Administrador',
  regulator: 'Regulador',
  hospital_operator: 'Operador Hospitalar',
  viewer: 'Visualizador',
};

export const ACTION_MAP: Record<string, string> = {
  reserve: 'Reservar',
  release: 'Liberar',
  occupy: 'Ocupar',
  block: 'Bloquear',
  maintenance: 'Manutenção',
};
