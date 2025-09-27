import { useCustomMutation, useEntityById } from '@/hooks';

import {
  publicationFormApiService,
  publicationFormService,
} from '../services/publicationFormService';
import type {
  AlliedMaterialsAreaPayload,
} from '../types/publication-form';

export const usePublicationFormById = (
  id: string,
  options: {
    enabled: boolean;
  },
) => {
  return useEntityById('admin-publication-form', publicationFormApiService, id, options);
};

// * Allied Materials Area

export const useCreateAlliedMaterialsArea = () => {
  return useCustomMutation((data: AlliedMaterialsAreaPayload) =>
    publicationFormService.createAlliedMaterialsArea(data),
  );
};

export const useUpdateAlliedMaterialsArea = () => {
  return useCustomMutation((data: { id: string } & AlliedMaterialsAreaPayload) =>
    publicationFormService.updateAlliedMaterialsArea(data.id, data),
  );
};
