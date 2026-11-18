SEARCH_ANIME_QUERY = """
query ($search: String, $page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      currentPage
      perPage
      hasNextPage
      total
    }
    media(
      search: $search,
      type: ANIME,
      sort: SEARCH_MATCH
    ) {
      id
      title {
        romaji
        english
        native
      }
      coverImage {
        large
      }
      episodes
      status
      averageScore
    }
  }
}
"""

ANIME_DETAIL_QUERY = """
query ($id: Int!) {
    Media(id: $id, type: ANIME){
    id
    title {
      romaji
      english
      native
    }
    coverImage{
      large
    }
    episodes
    status
    averageScore
    description
  }
}
"""