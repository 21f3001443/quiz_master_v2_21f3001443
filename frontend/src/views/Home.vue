<template>
    <HeaderBar />
    <div class="container d-flex justify-content-center text-center">
        <div class="row">
            <div class="col-sm-6 mb-3 mb-sm-0">
                <div v-for="s in [ { 'subject_name': 'Math', 'subject_description': 'Mathematics', 'chapters': [ { 'chapter_id': 1, 'chapter_name': 'Algebra', 'chapter_description': 'Algebra Basics', 'questions': [ { 'question_id': 1, 'question_text': 'What is 2 + 2?', 'options': [ { 'option_id': 1, 'option_text': '3', 'is_correct': false }, { 'option_id': 2, 'option_text': '4', 'is_correct': true } ] } ] } ] } ]" class="card border-secondary mb-3" style="width: 60rem; margin: 5rem 1rem;">
                    <div class="card-header">
                        <figure class="text-center">
                            <blockquote class="blockquote">
                                <h2><span class="badge text-bg-warning">Subject: {{ s.subject_name }}</span></h2>
                            </blockquote>
                            <figcaption class="blockquote-footer">
                                {{ s.subject_description }}
                            </figcaption>
                        </figure>
                    </div>
                    <div class="card-body text-secondary">
                        <table class="table table-bordered border-secondary">
                            <thead>
                                <tr>
                                    <th scope="col" style="align-items: center;">Chapter name</th>
                                    <th scope="col" style="align-items: center;">No. of questions</th>
                                    <th scope="col" style="align-items: center;">Action</th>
                                </tr>
                            </thead>
                            <tbody v-for="c in s.chapters" class="table-group-divider">
                                    <tr>
                                        <td>
                                            <button type="button" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#{{ c.chapter_id }}">
                                                {{ c.chapter_name }}
                                            </button>
                                            <div class="modal fade" id="{{ c.chapter_id }}" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="{{ c.chapter_id }}Label" aria-hidden="true">
                                                <div class="modal-dialog">
                                                <div class="modal-content">
                                                    <div class="modal-header">
                                                    <h1 class="modal-title fs-5" id="{{ c.chapter_id }}Label">{{ c.chapter_name }}</h1>
                                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                    </div>
                                                    <div class="modal-body">
                                                        {{ c.chapter_description }}
                                                    </div>
                                                    <div class="modal-footer">
                                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                                    </div>
                                                </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <button type="button" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#no_of_{{ c.chapter_id }}">
                                                {{ c.questions | length }}
                                            </button>
                                            <div class="modal fade" id="no_of_{{ c.chapter_id }}" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="no_of_{{ c.chapter_id }}Label" aria-hidden="true">
                                                <div class="modal-dialog modal-xl">
                                                <div class="modal-content">
                                                    <div class="modal-header">
                                                    <h1 class="modal-title fs-5" id="no_of_{{ c.chapter_id }}Label">{{ c.chapter_name }}</h1>
                                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                    </div>
                                                    <div class="modal-body">
                                                        <table class="table table-bordered border-secondary">
                                                            <thead>
                                                                <tr>
                                                                    <th scope="col" style="align-items: center;">Type of Question</th>
                                                                    <th scope="col" style="align-items: center;">Question statement</th>
                                                                    <th scope="col" style="align-items: center;">Action</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody v-for="q in c.questions">
                                                                    <tr>
                                                                        <td>{{ q.question_title }}</td>
                                                                        <td>{{ q.question_statement }}</td>
                                                                        <td>
                                                                            <a href="/question/update?question_id={{ q.question_id }}" class="link-body-emphasis link-offset-2 link-underline-opacity-25 link-underline-opacity-75-hover">Edit</a>
                                                                            <a href="/question/delete?question_id={{ q.question_id }}" class="link-body-emphasis link-offset-2 link-underline-opacity-25 link-underline-opacity-75-hover">Delete</a>
                                                                        </td>
                                                                    </tr>
                                                                {% endfor %}
                                                            </tbody>
                                                        </table>
                                                        <a href="/question/create?chapter_id={{c.chapter_id}}" class="btn btn-secondary" tabindex="-1" role="button" aria-disabled="true">+ Question</a>
                                                    </div>
                                                    <div class="modal-footer">
                                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                                    </div>
                                                </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <a href="/chapter/update?chapter_id={{ c.chapter_id }}&subject_name={{ s.subject_name }}" class="link-body-emphasis link-offset-2 link-underline-opacity-25 link-underline-opacity-75-hover">Edit</a>
                                            <a href="/chapter/delete?chapter_id={{ c.chapter_id }}" class="link-body-emphasis link-offset-2 link-underline-opacity-25 link-underline-opacity-75-hover">Delete</a>
                                        </td>
                                    </tr>
                            </tbody>
                        </table>
                        <div style="padding: 1rem;">
                            <a href="/subject/update?subject_id={{ s.subject_id }}" class="btn btn-secondary" tabindex="-1" role="button" aria-disabled="true">Edit</a>
                            <a href="/subject/delete?subject_id={{ s.subject_id }}" class="btn btn-secondary" tabindex="-1" role="button" aria-disabled="true">Delete</a>
                            <a href="/chapter/create?subject_id={{ s.subject_id }}" class="btn btn-secondary" tabindex="-1" role="button" aria-disabled="true">+ Chapter</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="container d-flex justify-content-center text-center" style="padding: 1rem; margin-top: 5rem;">
        <a href="/subject/create" class="btn btn-secondary" tabindex="-1" role="button" aria-disabled="true">+ Subject</a>
    </div>
</template>


<script>
import HeaderBar from '@/components/HeaderBar.vue';

export default {
    name: 'Home',
    components: {
        HeaderBar
    }
}
</script>