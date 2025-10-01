import { Button, Textarea, Text, Title, Box, NativeSelect } from '@mantine/core';
import { useForm } from '@mantine/form';
import { DangerLevels } from '../DangerLevels/DangerLevels';
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
    const { forecast, handleSubmit, summary, models } = useSummaryTextForm(form.reset);

    return (
        <Box>
            <Title fz="lg" c="white">Summary Text Form</Title>    
            <form onSubmit={form.onSubmit((values) => handleSubmit(values.summaryText, values.model))}>
                <NativeSelect c="white" {...form.getInputProps('model')} data={models} label="Model" />
                <Textarea c="white" label="Summary Text" {...form.getInputProps('summaryText')} />
                <Button mt="md" variant="default" color='myColor.5' type="submit">Submit</Button>
            </form>
            {(summary && forecast) && (
                <>
                    <Text>{summary}</Text>
                    <DangerLevels levels={forecast?.levels || {}} />
                </>
            )}
        </Box>
    );
}