# Convencion de JS Movil

Esta carpeta contiene scripts para vistas moviles.

## Estructura base

- `static/assets/dist/js/movil/<modulo>/<nombre_vista>_movil.js`

Ejemplo actual:

- `static/assets/dist/js/movil/shop_products/move_shop_products_auto_movil.js`

## Reglas de nombres

- Sufijo obligatorio: `_movil.js`
- Mantener el mismo nombre base que el template movil.

## Enlace desde template

En el template movil correspondiente, usar:

```django
<script src="{% static 'assets/dist/js/movil/<modulo>/<nombre_vista>_movil.js' %}"></script>
```

## Recomendaciones

- Reutilizar logica del flujo desktop cuando sea posible.
- Priorizar interacciones tactiles y componentes livianos.
- Evitar dependencias no usadas para reducir carga en movil.
