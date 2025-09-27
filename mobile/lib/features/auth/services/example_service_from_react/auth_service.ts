import { createApiService } from '@/services/crud';

import type {
  AlliedMaterialsAreaPayload,
  IdentityStatementAreaPayload,
  PublicationForm,
} from '../types/publication-form';

export const publicationFormApiService = createApiService<PublicationForm>(
  '/admin/archive-management/publication-form',
);

export const publicationFormService = {
  async createAlliedMaterialsArea(data: AlliedMaterialsAreaPayload) {
    return publicationFormApiService.customPost(`/allied-materials-area`, data);
  },

  async updateAlliedMaterialsArea(id: string, data: AlliedMaterialsAreaPayload) {
    return publicationFormApiService.customPost(`allied-materials-area/${id}`, data);
  },
};
