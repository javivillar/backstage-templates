/** Roles of the ${{ values.name }} in the Keycloak realm. The API enforces them; here they only hide. */
export const VIEWER = '${{ values.name }}-viewer';
export const ADMIN = '${{ values.name }}-admin';
