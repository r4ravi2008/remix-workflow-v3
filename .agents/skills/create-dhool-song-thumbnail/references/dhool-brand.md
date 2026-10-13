# Dhool thumbnail system

- Canvases: 1280x720, 16:9 for YouTube; 1080x1920, 9:16 for Instagram Reels.
- Artwork: cinematic neon or nocturnal poster treatment derived from the song theme.
- Identity: preserve source-video facial structure; stylization must not replace actors or performers with generic characters.
- YouTube composition: reserve the left side for text; place the principal faces on the right or center-right.
- Instagram composition: recompose for portrait. Keep the principal faces, song title, genre, and source credit in the center-safe region. Use the top and bottom for nonessential atmosphere that can tolerate Reel UI or feed/profile cropping.
- Overlay authority: `assets/youtube/thumbnails/dhool-neon-cinema-v1/render-thumbnails.sh`.
- Shared labels: `DHOOL / <GENRE>`, song title, movie or verified source credit, and `TELUGU ELECTRONIC / DH_99`.
- Text: render deterministically after image generation. Generated artwork contains no lettering.
- Mobile gates: title and principal faces must remain readable/recognizable at 320x180 for YouTube and 180x320 for Instagram.
- Pairing gate: both covers use the same approved identities, palette, title spelling, genre, and source credit, but neither is a mechanical crop or stretch of the other.
- Live gate: reopening must show a changed CDN version, then the downloaded live image must match the local final at normalized RMSE <= 0.06.
