# TagLinks

#### Créer un Tag

```bash
curl -X POST http://localhost:5000/tags \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"name": "Important", "color": "#FF0000"}'
```

#### Lister Tous les Tags

```bash
curl -X GET http://localhost:5000/tags \
    -H "Authorization: Bearer <TOKEN>"
```

#### Obtenir un Tag par ID

```bash
curl -X GET http://localhost:5000/tags/<TAG_ID> \
    -H "Authorization: Bearer <TOKEN>"
```

#### Mettre à Jour un Tag

```bash
curl -X PUT http://localhost:5000/tags/<TAG_ID> \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"color": "#00FF00"}'
```

#### Supprimer un Tag

```bash
curl -X DELETE http://localhost:5000/tags/<TAG_ID> \
    -H "Authorization: Bearer <TOKEN>"
```

- **Créer un link** :

  ```bash
  curl -X POST http://localhost:5000/links \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Mon Site",
      "description": "Ceci est une description",
      "url": "https://example.com",
      "tag_ids": ["<TAG_ID_1>", "<TAG_ID_2>"]
    }'
  ```

- **Lister les links** :

  ```bash
  curl -X GET http://localhost:5000/links \
    -H "Authorization: Bearer <TOKEN>"
  ```

- **Obtenir un link spécifique** :

  ```bash
  curl -X GET http://localhost:5000/links/<LINK_ID> \
    -H "Authorization: Bearer <TOKEN>"
  ```

- **Mettre à jour un link** :

  ```bash
  curl -X PUT http://localhost:5000/links/<LINK_ID> \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"description": "Nouvelle description", "tag_ids": ["<NEW_TAG_ID_1>"]}'
  ```

- **Supprimer un link** :

  ```bash
  curl -X DELETE http://localhost:5000/links/<LINK_ID> \
    -H "Authorization: Bearer <TOKEN>"
  ```

- **Recherche de liens avec une limite**

  ```bash
  curl -X POST http://localhost:5000/links/search-by-tags \
      -H "Authorization: Bearer <TOKEN>" \
      -H "Content-Type: application/json" \
      -d '{
          "tag_ids": ["<TAG_ID_1>", "<TAG_ID_2>"],
          "limit": 10
      }'
  ```

---

### Commande Docker pour créer un conteneur MongoDB

Vous pouvez exécuter la commande suivante pour lancer un conteneur MongoDB :

```bash
docker run -d --name mongodb-container \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo
```

#### Explications :

- `-d` : Lance le conteneur en arrière-plan (mode détaché).
- `--name mongodb-container` : Nomme le conteneur.
- `-p 27017:27017` : Expose le port 27017 (le port par défaut de MongoDB) du conteneur sur l'hôte.
- `-e MONGO_INITDB_ROOT_USERNAME=admin` : Définit l'utilisateur administrateur.
- `-e MONGO_INITDB_ROOT_PASSWORD=password` : Définit le mot de passe administrateur.
- `mongo` : Utilise l'image officielle MongoDB.

---
