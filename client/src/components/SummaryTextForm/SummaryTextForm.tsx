import { Button, Textarea, Text, Title, Box, NativeSelect, Loader } from '@mantine/core';
import { useForm } from '@mantine/form';
import { LevelTable } from '../LevelTable/LevelTable';
import { useSummaryTextForm } from './hooks/useSummaryTextForm';    

export function SummaryTextForm() {
    const form = useForm({
        initialValues: {
            summaryText: '',
            model: 'tfidf_mlp',
        },
        validate: {
            summaryText: (value) => value.length > 0 ? null : 'Summary text is required',
        },
    });
    const { forecast, handleSubmit, summary, models, loading } = useSummaryTextForm(form.reset);

    return (
        <Box style={{ borderBottom: '8px solid var(--mantine-color-myColor-5)' }} pb="xl">
            <Title mb="sm" mt="md" fz="xl" c="white">Danger Level Prediction</Title> 
            <Text c="white">Enter a summary text to get a forecast.</Text>   
            <form onSubmit={form.onSubmit((values) => handleSubmit(values.summaryText, values.model))}>
                <NativeSelect mt="sm" mb="sm" c="white" {...form.getInputProps('model')} data={models} label="Model" />
                <Textarea c="white" label="Summary Text" {...form.getInputProps('summaryText')} />
                <Button mt="md" variant="outline" color='myColor.2' type="submit">Submit</Button>
            </form>
            {loading && <Loader color="white" />}
            {(summary && forecast && !loading) && (
                <>
                    <Title fz="lg" c="white" mt="lg" mb="sm">Summary</Title>
                    <Text mb="sm" c="white">{summary}</Text>
                    <LevelTable prediction={forecast} />
                </>
            )}
        </Box>
    );
}